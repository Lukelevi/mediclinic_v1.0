from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from models import db, Doctor
from flask_bcrypt import check_password_hash
import jwt
import datetime
from functools import wraps

auth_bp = Blueprint('auth', __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            # Remove 'Bearer ' prefix if present
            if token.startswith('Bearer '):
                token = token[7:]
            
            data = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=["HS256"])
            current_user = Doctor.query.get(data['user_id'])
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Check if doctor already exists
    if Doctor.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Doctor already exists with this email'}), 400
    
    if Doctor.query.filter_by(license_number=data['license_number']).first():
        return jsonify({'message': 'Doctor already exists with this license number'}), 400
    
    # Create new doctor
    doctor = Doctor(
        first_name=data['first_name'],
        last_name=data['last_name'],
        email=data['email'],
        phone=data.get('phone'),
        specialty=data.get('specialty'),
        license_number=data['license_number']
    )
    
    doctor.set_password(data['password'])
    
    db.session.add(doctor)
    db.session.commit()
    
    return jsonify({
        'message': 'Doctor registered successfully',
        'doctor': doctor.to_dict()
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    doctor = Doctor.query.filter_by(email=data['email']).first()
    
    if not doctor or not doctor.check_password(data['password']):
        return jsonify({'message': 'Invalid email or password'}), 401
    
    if not doctor.is_active:
        return jsonify({'message': 'Account is deactivated'}), 401
    
    # Generate JWT token
    token = jwt.encode({
        'user_id': doctor.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }, current_app.config['JWT_SECRET_KEY'])
    
    login_user(doctor)
    
    return jsonify({
        'message': 'Login successful',
        'token': token,
        'doctor': doctor.to_dict()
    }), 200

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logout successful'}), 200

@auth_bp.route('/me', methods=['GET'])
@login_required
def get_current_user():
    return jsonify(current_user.to_dict()), 200