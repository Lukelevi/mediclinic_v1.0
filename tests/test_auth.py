import pytest
import json
from models import Doctor

def test_doctor_registration(client):
    """Test doctor registration endpoint"""
    data = {
        'first_name': 'John',
        'last_name': 'Smith',
        'email': 'john.smith@hospital.com',
        'password': 'securepassword123',
        'license_number': 'MED123456',
        'specialty': 'Cardiology',
        'phone': '+1234567890'
    }
    
    response = client.post('/api/auth/register', 
                          data=json.dumps(data),
                          content_type='application/json')
    
    assert response.status_code == 201
    response_data = json.loads(response.data)
    assert response_data['message'] == 'Doctor registered successfully'
    assert 'doctor' in response_data
    
    # Verify doctor exists in database
    doctor = Doctor.query.filter_by(email=data['email']).first()
    assert doctor is not None
    assert doctor.first_name == data['first_name']

def test_doctor_login(client, create_test_doctor):
    """Test doctor login endpoint"""
    data = {
        'email': 'test@doctor.com',
        'password': 'password123'
    }
    
    response = client.post('/api/auth/login',
                          data=json.dumps(data),
                          content_type='application/json')
    
    assert response.status_code == 200
    response_data = json.loads(response.data)
    assert 'token' in response_data
    assert response_data['message'] == 'Login successful'

def test_login_invalid_credentials(client, create_test_doctor):
    """Test login with invalid credentials"""
    data = {
        'email': 'test@doctor.com',
        'password': 'wrongpassword'
    }
    
    response = client.post('/api/auth/login',
                          data=json.dumps(data),
                          content_type='application/json')
    
    assert response.status_code == 401
    response_data = json.loads(response.data)
    assert 'Invalid email or password' in response_data['message']

def test_get_current_doctor(client, create_test_doctor, auth_headers):
    """Test getting current doctor info"""
    # First login to get token
    login_data = {'email': 'test@doctor.com', 'password': 'password123'}
    login_response = client.post('/api/auth/login',
                                data=json.dumps(login_data),
                                content_type='application/json')
    token = json.loads(login_response.data)['token']
    
    # Get current doctor info
    response = client.get('/api/auth/me',
                         headers=auth_headers(token))
    
    assert response.status_code == 200
    response_data = json.loads(response.data)
    assert response_data['email'] == 'test@doctor.com'