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


@bp.route('', methods=['GET'])
@jwt_required()
def get_projects():
    """Get all of the user's projects."""
    try:
        user_id = int(get_jwt_identity())
        projects = Project.query.filter_by(
            user_id=user_id).order_by(Project.name.asc()).all()
        project_data = [{'id': p.id, 'name': p.name,
                         'description': p.description} for p in projects]
        return jsonify({'success': True, 'data': {'projects': project_data}}), 200
    except Exception as e:
        logging.error(
            f"Failed to get projects for user {get_jwt_identity()}. Error: {e}", exc_info=True)
        return jsonify({'success': False, 'message': 'An internal server error occurred.'}), 500


@bp.route('/<int:project_id>', methods=['PUT'])
@jwt_required()
def update_project(project_id):
    """Update an existing project."""
    try:
        user_id = int(get_jwt_identity())
        project = Project.query.filter_by(
            id=project_id, user_id=user_id).first_or_404()
        data = request.get_json()

        project.name = data.get('name', project.name)
        project.description = data.get('description', project.description)

        db.session.commit()
        return jsonify({'success': True, 'message': 'Project updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        logging.error(
            f"Project update failed for user {get_jwt_identity()}. Error: {e}", exc_info=True)
        return jsonify({'success': False, 'message': 'An internal server error occurred.'}), 500


@bp.route('/<int:project_id>', methods=['DELETE'])
@jwt_required()
def delete_project(project_id):
    """Delete a project and its associated tasks."""
    try:
        user_id = int(get_jwt_identity())
        project = Project.query.filter_by(
            id=project_id, user_id=user_id).first_or_404()

        # Manually delete associated tasks
        for task in project.tasks:
            db.session.delete(task)

        db.session.delete(project)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Project and associated tasks deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        logging.error(
            f"Project deletion failed for user {get_jwt_identity()}. Error: {e}", exc_info=True)
        return jsonify({'success': False, 'message': 'An internal server error occurred.'}), 500
