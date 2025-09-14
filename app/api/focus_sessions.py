# app/api/focus_sessions.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import db
from ..models.focus_session import FocusSession
from datetime import datetime

bp = Blueprint('focus_sessions', __name__)


@bp.route('/start', methods=['POST'])
@jwt_required()
def start_session():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    task_id = data.get('task_id')

    session = FocusSession(
        user_id=user_id,
        task_id=task_id,
        duration=0,
        started_at=datetime.utcnow()  # Make sure to set the start time
    )
    db.session.add(session)
    db.session.commit()

    return jsonify({'success': True, 'session_id': session.id}), 201


@bp.route('/<int:session_id>/stop', methods=['POST'])
@jwt_required()
def stop_session(session_id):
    user_id = int(get_jwt_identity())
    session = FocusSession.query.filter_by(
        id=session_id, user_id=user_id).first_or_404()

    session.ended_at = datetime.utcnow()
    duration = (session.ended_at - session.started_at).total_seconds() / 60
    session.duration = int(duration)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Session stopped'}), 200
