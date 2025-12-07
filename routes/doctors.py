from flask import Blueprint, request, jsonify
from flask_login import login_required
from models import db, Doctor
from functools import wraps

doctors_bp = Blueprint('doctors', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Add admin check logic here if needed
        # For now, just require login
        return f(*args, **kwargs)
    return decorated_function

@doctors_bp.route('/', methods=['GET'])
@login_required
def get_doctors():
    doctors = Doctor.query.filter_by(is_active=True).all()
    return jsonify([doctor.to_dict() for doctor in doctors]), 200

@doctors_bp.route('/<int:doctor_id>', methods=['GET'])
@login_required
def get_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    return jsonify(doctor.to_dict()), 200

@doctors_bp.route('/<int:doctor_id>', methods=['PUT'])
@login_required
def update_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    data = request.get_json()
    
    # Update fields
    if 'first_name' in data:
        doctor.first_name = data['first_name']
    if 'last_name' in data:
        doctor.last_name = data['last_name']
    if 'phone' in data:
        doctor.phone = data['phone']
    if 'specialty' in data:
        doctor.specialty = data['specialty']
    if 'password' in data:
        doctor.set_password(data['password'])
    
    db.session.commit()
    
    return jsonify({
        'message': 'Doctor updated successfully',
        'doctor': doctor.to_dict()
    }), 200

@doctors_bp.route('/<int:doctor_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    doctor.is_active = False
    db.session.commit()
    
    return jsonify({'message': 'Doctor deactivated successfully'}), 200