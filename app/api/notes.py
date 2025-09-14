from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import db
from ..models.note import Note

bp = Blueprint('notes', __name__)


@bp.route('', methods=['GET'])
@jwt_required()
def get_notes():
    user_id = int(get_jwt_identity())
    notes = Note.query.filter_by(user_id=user_id).all()
    return jsonify({'success': True, 'data': {'notes': [{'id': note.id, 'content': note.content} for note in notes]}}), 200


bp = Blueprint('notes', __name__)


@bp.route('', methods=['POST'])
@jwt_required()
def create_note():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    note = Note(content=data['content'],
                user_id=user_id, project_id=data['project_id'])
    db.session.add(note)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Note created successfully'}), 201
