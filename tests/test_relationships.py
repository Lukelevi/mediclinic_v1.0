#Test Foreign Key
import pytest
from models import Doctor, Patient

def test_doctor_patient_relationship(app, create_test_doctor, create_test_patient):
    """Test foreign key relationship between doctor and patient"""
    with app.app_context():
        doctor = create_test_doctor
        patient = create_test_patient
        
        # Test relationship from patient to doctor
        assert patient.doctor_id == doctor.id
        assert patient.doctor == doctor
        
        # Test relationship from doctor to patients
        assert len(doctor.patients) == 1
        assert doctor.patients[0] == patient
        
        # Test cascade delete (if configured)
        db.session.delete(doctor)
        db.session.commit()
        
        # Patient should be deleted if cascade is set
        patient = Patient.query.get(create_test_patient.id)
        assert patient is None

def test_multiple_patients_per_doctor(app, create_test_doctor):
    """Test that one doctor can have multiple patients"""
    with app.app_context():
        doctor = create_test_doctor
        
        # Create multiple patients
        patient1 = Patient(
            first_name='Patient1',
            last_name='Doe',
            date_of_birth=datetime(1990, 1, 1).date(),
            gender='Male',
            doctor_id=doctor.id
        )
        
        patient2 = Patient(
            first_name='Patient2',
            last_name='Smith',
            date_of_birth=datetime(1985, 1, 1).date(),
            gender='Female',
            doctor_id=doctor.id
        )
        
        db.session.add_all([patient1, patient2])
        db.session.commit()
        
        assert len(doctor.patients) == 2
        assert {p.first_name for p in doctor.patients} == {'Patient1', 'Patient2'}