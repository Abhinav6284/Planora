from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import db
from ..models.project import Project
import logging

bp = Blueprint('projects', __name__)


@bp.route('', methods=['POST'])
@jwt_required()
def create_project():
    """Create a new project."""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()

        if not data or not data.get('name'):
            return jsonify({'success': False, 'message': 'Project name is required'}), 400

        project = Project(
            name=data['name'],
            description=data.get('description', ''),
            user_id=user_id
        )
        db.session.add(project)
        db.session.commit()

        # We need to return the created project's data
        project_data = {'id': project.id, 'name': project.name,
                        'description': project.description}

        return jsonify({
            'success': True,
            'message': 'Project created successfully',
            'data': {'project': project_data}
        }), 201

    except Exception as e:
        db.session.rollback()
        logging.error(
            f"Project creation failed for user {get_jwt_identity()}. Error: {e}", exc_info=True)
        return jsonify({'success': False, 'message': 'An internal server error occurred.'}), 500

# We can add routes for getting, updating, and deleting projects here later.
