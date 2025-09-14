# app/api/profile.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import db
from ..models.user import User
import logging

bp = Blueprint('profile', __name__)


@bp.route('', methods=['GET'])
@jwt_required()
def get_profile():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    return jsonify({'success': True, 'data': user.to_dict(include_sensitive=True)}), 200


@bp.route('', methods=['PUT'])
@jwt_required()
def update_profile():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    data = request.get_json()

    # Update fields
    user.first_name = data.get('first_name', user.first_name)
    user.last_name = data.get('last_name', user.last_name)
    user.timezone = data.get('timezone', user.timezone)

    db.session.commit()
    return jsonify({'success': True, 'message': 'Profile updated successfully'}), 200
