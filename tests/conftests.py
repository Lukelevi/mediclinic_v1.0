import pytest
import json
from app import create_app, db
from models import Doctor, Patient
from datetime import datetime

@pytest.fixture
def app():
    """Create test application"""
    app = create_app('testing')
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SECRET_KEY': 'test-secret-key',
        'JWT_SECRET_KEY': 'test-jwt-key'
    })
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Test client"""
    return app.test_client()

@pytest.fixture
def auth_headers():
    """Create authenticated headers"""
    def _create_headers(token):
        return {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
    return _create_headers

@pytest.fixture
def create_test_doctor(app):
    """Create test doctor in database"""
    with app.app_context():
        doctor = Doctor(
            first_name='Test',
            last_name='Doctor',
            email='test@doctor.com',
            license_number='TEST123',
            specialty='General'
        )
        doctor.set_password('password123')
        db.session.add(doctor)
        db.session.commit()
        return doctor

@pytest.fixture
def create_test_patient(app, create_test_doctor):
    """Create test patient in database"""
    with app.app_context():
        patient = Patient(
            first_name='John',
            last_name='Doe',
            date_of_birth=datetime(1990, 1, 1).date(),
            gender='Male',
            email='john@patient.com',
            phone='1234567890',
            doctor_id=create_test_doctor.id
        )
        db.session.add(patient)
        db.session.commit()
        return patient