from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash
from datetime import datetime
from ..extensions import db
from ..models.user import User
from ..models.task import Task

bp = Blueprint('auth', __name__)


@bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()

        # Validate required fields
        if not data or not all(k in data for k in ['username', 'email', 'password']):
            return jsonify({
                'success': False,
                'message': 'Username, email, and password are required'
            }), 400

        # Check if user exists
        if User.query.filter_by(username=data['username']).first():
            return jsonify({
                'success': False,
                'message': 'Username already exists'
            }), 400

        if User.query.filter_by(email=data['email']).first():
            return jsonify({
                'success': False,
                'message': 'Email already registered'
            }), 400

        # Create new user
        user = User(
            username=data['username'],
            email=data['email'],
            first_name=data.get('first_name'),
            last_name=data.get('last_name')
        )
        user.set_password(data['password'])

        db.session.add(user)
        db.session.commit()

        # Create access token
        access_token = create_access_token(identity=str(user.id))

        return jsonify({
            'success': True,
            'message': 'User registered successfully',
            'data': {
                'access_token': access_token,
                'user': user.to_dict()
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Registration failed',
            'error': str(e)
        }), 500


@bp.route('/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()

        if not data or not all(k in data for k in ['username', 'password']):
            return jsonify({
                'success': False,
                'message': 'Username and password are required'
            }), 400

        # Find user
        user = User.query.filter_by(username=data['username']).first()

        if not user or not user.check_password(data['password']):
            return jsonify({
                'success': False,
                'message': 'Invalid username or password'
            }), 401

        # Update last login
        user.update_last_login()

        # Create access token
        access_token = create_access_token(identity=str(user.id))

        return jsonify({
            'success': True,
            'message': 'Login successful',
            'data': {
                'access_token': access_token,
                'user': user.to_dict(include_sensitive=True)
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Login failed',
            'error': str(e)
        }), 500


@bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user profile"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404

        return jsonify({
            'success': True,
            'data': {
                'user': user.to_dict(include_sensitive=True),
                'stats': user.get_task_stats()
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to get user profile',
            'error': str(e)
        }), 500
