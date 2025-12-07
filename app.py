from flask import Flask, jsonify
from flask_login import LoginManager
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from models import db, Doctor
from routes.auth import auth_bp
from routes.doctors import doctors_bp
from routes.patients import patients_bp
import os

def create_app():
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object('config.DevelopmentConfig')
    
    # Initialize extensions
    db.init_app(app)
    bcrypt = Bcrypt(app)
    CORS(app)
    
    # Flask-Login setup
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    @login_manager.user_loader
    def load_user(user_id):
        return Doctor.query.get(int(user_id))
    
    @login_manager.unauthorized_handler
    def unauthorized():
        return jsonify({'message': 'Unauthorized access'}), 401
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(doctors_bp, url_prefix='/api/doctors')
    app.register_blueprint(patients_bp, url_prefix='/api/patients')
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'message': 'Resource not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'message': 'Internal server error'}), 500
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    # Root endpoint
    @app.route('/')
    def index():
        return jsonify({
            'message': 'Hospital Management System API',
            'version': '1.0.0',
            'endpoints': {
                'auth': '/api/auth',
                'doctors': '/api/doctors',
                'patients': '/api/patients'
            }
        })
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)