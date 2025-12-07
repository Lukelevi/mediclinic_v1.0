from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import db, Patient, Doctor
from datetime import datetime

patients_bp = Blueprint('patients', __name__)

@patients_bp.route('/', methods=['GET'])
@login_required
def get_patients():
    # If doctor, get only their patients
    # If admin, get all patients
    if hasattr(current_user, 'is_admin') and current_user.is_admin:
        patients = Patient.query.all()
    else:
        patients = Patient.query.filter_by(doctor_id=current_user.id).all()
    
    return jsonify([patient.to_dict() for patient in patients]), 200

@patients_bp.route('/<int:patient_id>', methods=['GET'])
@login_required
def get_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    
    # Check if current doctor owns this patient
    if patient.doctor_id != current_user.id and not (hasattr(current_user, 'is_admin') and current_user.is_admin):
        return jsonify({'message': 'Access denied'}), 403
    
    return jsonify(patient.to_dict()), 200

@patients_bp.route('/', methods=['POST'])
@login_required
def create_patient():
    data = request.get_json()
    
    # Parse date
    dob = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
    
    # Verify doctor exists
    doctor_id = data.get('doctor_id', current_user.id)
    doctor = Doctor.query.get(doctor_id)
    if not doctor:
        return jsonify({'message': 'Doctor not found'}), 404
    
    # Create patient
    patient = Patient(
        first_name=data['first_name'],
        last_name=data['last_name'],
        date_of_birth=dob,
        gender=data.get('gender'),
        phone=data.get('phone'),
        email=data.get('email'),
        address=data.get('address'),
        emergency_contact=data.get('emergency_contact'),
        blood_type=data.get('blood_type'),
        allergies=data.get('allergies'),
        doctor_id=doctor_id
    )
    
    db.session.add(patient)
    db.session.commit()
    
    return jsonify({
        'message': 'Patient created successfully',
        'patient': patient.to_dict()
    }), 201

@patients_bp.route('/<int:patient_id>', methods=['PUT'])
@login_required
def update_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    
    # Check if current doctor owns this patient
    if patient.doctor_id != current_user.id and not (hasattr(current_user, 'is_admin') and current_user.is_admin):
        return jsonify({'message': 'Access denied'}), 403
    
    data = request.get_json()
    
    # Update fields
    if 'first_name' in data:
        patient.first_name = data['first_name']
    if 'last_name' in data:
        patient.last_name = data['last_name']
    if 'date_of_birth' in data:
        patient.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
    if 'gender' in data:
        patient.gender = data['gender']
    if 'phone' in data:
        patient.phone = data['phone']
    if 'email' in data:
        patient.email = data['email']
    if 'address' in data:
        patient.address = data['address']
    if 'emergency_contact' in data:
        patient.emergency_contact = data['emergency_contact']
    if 'blood_type' in data:
        patient.blood_type = data['blood_type']
    if 'allergies' in data:
        patient.allergies = data['allergies']
    if 'doctor_id' in data:
        # Verify new doctor exists
        doctor = Doctor.query.get(data['doctor_id'])
        if not doctor:
            return jsonify({'message': 'Doctor not found'}), 404
        patient.doctor_id = data['doctor_id']
    
    patient.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'message': 'Patient updated successfully',
        'patient': patient.to_dict()
    }), 200

@patients_bp.route('/<int:patient_id>', methods=['DELETE'])
@login_required
def delete_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    
    # Check if current doctor owns this patient
    if patient.doctor_id != current_user.id and not (hasattr(current_user, 'is_admin') and current_user.is_admin):
        return jsonify({'message': 'Access denied'}), 403
    
    db.session.delete(patient)
    db.session.commit()
    
    return jsonify({'message': 'Patient deleted successfully'}), 200