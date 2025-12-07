#Test my patient CRUD priinciples
import pytest
import json
from datetime import datetime
from models import Patient

def test_create_patient(client, create_test_doctor, auth_headers):
    """Test creating a new patient with doctor as foreign key"""
    # Login to get token
    login_data = {'email': 'test@doctor.com', 'password': 'password123'}
    login_response = client.post('/api/auth/login',
                                data=json.dumps(login_data),
                                content_type='application/json')
    token = json.loads(login_response.data)['token']
    
    # Create patient data
    patient_data = {
        'first_name': 'Jane',
        'last_name': 'Doe',
        'date_of_birth': '1990-05-15',
        'gender': 'Female',
        'email': 'jane.doe@email.com',
        'phone': '+1234567890',
        'doctor_id': create_test_doctor.id
    }
    
    response = client.post('/api/patients',
                          data=json.dumps(patient_data),
                          headers=auth_headers(token),
                          content_type='application/json')
    
    assert response.status_code == 201
    response_data = json.loads(response.data)
    assert response_data['message'] == 'Patient created successfully'
    
    # Verify patient was created with correct foreign key
    patient = Patient.query.filter_by(email='jane.doe@email.com').first()
    assert patient is not None
    assert patient.doctor_id == create_test_doctor.id

def test_get_patients_for_doctor(client, create_test_patient, auth_headers):
    """Test getting patients for specific doctor"""
    # Login to get token
    login_data = {'email': 'test@doctor.com', 'password': 'password123'}
    login_response = client.post('/api/auth/login',
                                data=json.dumps(login_data),
                                content_type='application/json')
    token = json.loads(login_response.data)['token']
    
    response = client.get('/api/patients',
                         headers=auth_headers(token))
    
    assert response.status_code == 200
    patients = json.loads(response.data)
    assert len(patients) == 1
    assert patients[0]['first_name'] == 'John'

def test_update_patient(client, create_test_patient, auth_headers):
    """Test updating patient information"""
    # Login to get token
    login_data = {'email': 'test@doctor.com', 'password': 'password123'}
    login_response = client.post('/api/auth/login',
                                data=json.dumps(login_data),
                                content_type='application/json')
    token = json.loads(login_response.data)['token']
    
    update_data = {
        'first_name': 'Johnathan',
        'phone': '+9876543210'
    }
    
    response = client.put(f'/api/patients/{create_test_patient.id}',
                         data=json.dumps(update_data),
                         headers=auth_headers(token),
                         content_type='application/json')
    
    assert response.status_code == 200
    response_data = json.loads(response.data)
    assert response_data['message'] == 'Patient updated successfully'
    
    # Verify update in database
    patient = Patient.query.get(create_test_patient.id)
    assert patient.first_name == 'Johnathan'
    assert patient.phone == '+9876543210'

def test_patient_not_found(client, auth_headers):
    """Test accessing non-existent patient"""
    # Login to get token
    login_data = {'email': 'test@doctor.com', 'password': 'password123'}
    login_response = client.post('/api/auth/login',
                                data=json.dumps(login_data),
                                content_type='application/json')
    token = json.loads(login_response.data)['token']
    
    response = client.get('/api/patients/999',
                         headers=auth_headers(token))
    
    assert response.status_code == 404

def test_create_patient_invalid_doctor(client, auth_headers):
    """Test creating patient with invalid doctor ID"""
    # Login to get token
    login_data = {'email': 'test@doctor.com', 'password': 'password123'}
    login_response = client.post('/api/auth/login',
                                data=json.dumps(login_data),
                                content_type='application/json')
    token = json.loads(login_response.data)['token']
    
    patient_data = {
        'first_name': 'Jane',
        'last_name': 'Doe',
        'date_of_birth': '1990-05-15',
        'gender': 'Female',
        'doctor_id': 999  # Non-existent doctor
    }
    
    response = client.post('/api/patients',
                          data=json.dumps(patient_data),
                          headers=auth_headers(token),
                          content_type='application/json')
    
    assert response.status_code == 404
    response_data = json.loads(response.data)
    assert 'Doctor not found' in response_data['message']