from flask import session
from ..extensions import db, oauth
from flask import Blueprint, request, jsonify, url_for, redirect
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import datetime
from ..extensions import db
from ..models.user import User
import logging

bp = Blueprint('auth', __name__)


@bp.route('/register', methods=['POST'])
def register():
    """
    Handles new user registration with an extended set of fields.
    Validates all inputs and creates a new user.
    """
    try:
        data = request.get_json()

        # --- Comprehensive Validation ---
        required_fields = ['first_name', 'last_name',
                           'username', 'email', 'password', 'confirm_password']
        if not all(field in data and data[field] for field in required_fields):
            return jsonify({'success': False, 'message': 'Please fill out all required fields.'}), 400

        if data['password'] != data['confirm_password']:
            return jsonify({'success': False, 'message': 'Passwords do not match.'}), 400

        if User.query.filter_by(username=data['username']).first():
            return jsonify({'success': False, 'message': 'Username is already taken.'}), 400

        if User.query.filter_by(email=data['email']).first():
            return jsonify({'success': False, 'message': 'Email is already registered.'}), 400

        # Check for phone number uniqueness if provided
        if data.get('phone_number') and User.query.filter_by(phone_number=data['phone_number']).first():
            return jsonify({'success': False, 'message': 'Phone number is already in use.'}), 400

        # --- User Creation ---
        user = User(
            first_name=data['first_name'],
            last_name=data['last_name'],
            username=data['username'],
            email=data['email'],
            phone_number=data.get('phone_number'),
            referral_source=data.get('referral_source')
        )
        user.set_password(data['password'])
        user.start_trial()  # Start the Founder's Program trial

        db.session.add(user)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Registration successful! Please log in.'}), 201

    except Exception as e:
        db.session.rollback()
        logging.error(f"Registration failed: {e}", exc_info=True)
        return jsonify({'success': False, 'message': 'An internal error occurred during registration.'}), 500


@bp.route('/login', methods=['POST'])
def login():
    """
    Handles user login using either username or email.
    """
    try:
        data = request.get_json()

        if not data or not data.get('login_identifier') or not data.get('password'):
            return jsonify({
                'success': False,
                'message': 'Username/Email and password are required'
            }), 400

        login_identifier = data.get('login_identifier')

        if '@' in login_identifier:
            user = User.query.filter_by(email=login_identifier).first()
        else:
            user = User.query.filter_by(username=login_identifier).first()

        if not user or not user.check_password(data.get('password')):
            return jsonify({
                'success': False,
                'message': 'Invalid credentials. Please try again.'
            }), 401

        user.update_last_login()
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
        logging.error(
            f"Login failed for identifier: {data.get('login_identifier')}. Error: {e}", exc_info=True)
        return jsonify({'success': False, 'message': 'Login failed due to an internal server error.'}), 500


@bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():

    user_id_str = get_jwt_identity()
    user = User.query.get(int(user_id_str))
    if not user:
        return jsonify({'success': False, 'message': 'User not found'}), 404
    return jsonify({
        'success': True,
        'data': {
            'user': user.to_dict(include_sensitive=True),
            'stats': user.get_task_stats()
        }
    }), 200


@bp.route('/login/google')
def google_login():
    redirect_uri = url_for('auth.google_authorize', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@bp.route('/authorize/google')
def google_authorize():
    token = oauth.google.authorize_access_token()

    nonce = session.get('google_nonce')
    user_info = oauth.google.parse_id_token(token, nonce=nonce)

    google_id = user_info['sub']
    user = User.query.filter_by(google_id=google_id).first()

    if not user:
        user = User.query.filter_by(email=user_info['email']).first()
        if not user:
            user = User(
                google_id=google_id,
                email=user_info['email'],
                first_name=user_info.get('given_name'),
                last_name=user_info.get('family_name'),
                username=user_info.get('email').split(
                    '@')[0],  # Or generate a unique username
                avatar_url=user_info.get('picture')
            )
            db.session.add(user)
        else:
            user.google_id = google_id
        db.session.commit()

    access_token = create_access_token(identity=str(user.id))
    # Redirect to the dashboard with the token
    return redirect(f'/dashboard?token={access_token}')


@bp.route('/login/github')
def github_login():
    redirect_uri = url_for('auth.github_authorize', _external=True)

    # --- ADD THIS LINE FOR DEBUGGING ---
    print(f"--- GitHub Redirect URI --- : {redirect_uri}")

    return oauth.github.authorize_redirect(redirect_uri)


@bp.route('/authorize/github')
def github_authorize():
    token = oauth.github.authorize_access_token()
    resp = oauth.github.get('user', token=token)
    profile = resp.json()

    github_id = str(profile['id'])
    user = User.query.filter_by(github_id=github_id).first()

    if not user:
        user_email = profile.get('email')

        # If the user has an email, check if an account with that email already exists
        if user_email:
            user = User.query.filter_by(email=user_email).first()

        if not user:
            # Create a new user if no existing user is found
            user = User(
                github_id=github_id,
                email=user_email,  # This can now be None
                username=profile.get('login'),
                first_name=profile.get('name', '').split(' ')[0],
                last_name=' '.join(profile.get('name', '').split(' ')[1:]),
                avatar_url=profile.get('avatar_url')
            )
            db.session.add(user)
        else:
            # If a user with that email exists, link their GitHub ID to it
            user.github_id = github_id

        db.session.commit()

    access_token = create_access_token(identity=str(user.id))
    return redirect(f'/dashboard?token={access_token}')
