from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import db
from ..models.task import Task
from ..models.project import Project
from datetime import datetime
import logging

bp = Blueprint('tasks', __name__)


@bp.route('', methods=['POST'])
@jwt_required()
def create_task():
    """Create a new task, optionally linking it to a project and category."""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()

        if not data or not data.get('title'):
            return jsonify({'success': False, 'message': 'Task title is required'}), 400

        # Validate that the project belongs to the user
        project_id = data.get('project_id')
        if project_id:
            project = Project.query.filter_by(
                id=project_id, user_id=user_id).first()
            if not project:
                return jsonify({'success': False, 'message': 'Project not found or you do not have permission.'}), 404

        # Parse due_date if it exists
        due_date = datetime.fromisoformat(data['due_date'].replace(
            'Z', '+00:00')) if data.get('due_date') else None

        task = Task(
            title=data['title'],
            description=data.get('description', ''),
            priority=data.get('priority', 'medium'),
            status=data.get('status', 'todo'),
            due_date=due_date,
            estimated_duration=data.get('estimated_duration'),
            user_id=user_id,
            # We'll add category validation later
            category_id=data.get('category_id')
        )

        if project_id:
            task.projects.append(project)

        db.session.add(task)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Task created', 'data': {'task': task.to_dict()}}), 201

    except Exception as e:
        db.session.rollback()
        logging.error(
            f"Task creation failed for user {user_id}. Error: {e}", exc_info=True)
        return jsonify({'success': False, 'message': 'An internal server error occurred.'}), 500


@bp.route('', methods=['GET'])
@jwt_required()
def get_tasks():
    """Get user's tasks, with optional filtering by project."""
    try:
        user_id = int(get_jwt_identity())
        project_id = request.args.get('project_id', type=int)

        query = Task.query.filter_by(user_id=user_id)

        if project_id:
            query = query.join(Task.projects).filter(Project.id == project_id)

        tasks = query.order_by(Task.created_at.desc()).all()

        return jsonify({'success': True, 'data': {'tasks': [task.to_dict() for task in tasks]}}), 200

    except Exception as e:
        logging.error(
            f"Failed to get tasks for user {user_id}. Error: {e}", exc_info=True)
        return jsonify({'success': False, 'message': 'An internal server error occurred.'}), 500


@bp.route('/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    """Update an existing task."""
    try:
        user_id = int(get_jwt_identity())
        task = Task.query.filter_by(id=task_id, user_id=user_id).first_or_404()
        data = request.get_json()

        # Update simple fields
        for field in ['title', 'description', 'priority', 'status', 'estimated_duration']:
            if field in data:
                setattr(task, field, data[field])

        if 'due_date' in data:
            task.due_date = datetime.fromisoformat(data['due_date'].replace(
                'Z', '+00:00')) if data.get('due_date') else None

        if 'project_id' in data:
            project = Project.query.filter_by(
                id=data['project_id'], user_id=user_id).first()
            if project:
                task.projects = [project]
            else:
                return jsonify({'success': False, 'message': 'Project not found or you do not have permission.'}), 404

        if data.get('status') == 'completed':
            task.mark_completed()

        db.session.commit()

        return jsonify({'success': True, 'message': 'Task updated', 'data': {'task': task.to_dict()}}), 200

    except Exception as e:
        db.session.rollback()
        logging.error(
            f"Task update failed for user {user_id}, task {task_id}. Error: {e}", exc_info=True)
        return jsonify({'success': False, 'message': 'An internal server error occurred.'}), 500


@bp.route('/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    """Delete a task."""
    try:
        user_id = int(get_jwt_identity())
        task = Task.query.filter_by(id=task_id, user_id=user_id).first_or_404()

        db.session.delete(task)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Task deleted successfully'}), 200

    except Exception as e:
        db.session.rollback()
        logging.error(
            f"Task deletion failed for user {user_id}, task {task_id}. Error: {e}", exc_info=True)
        return jsonify({'success': False, 'message': 'An internal server error occurred.'}), 500


@bp.route('/reorder', methods=['PUT'])
@jwt_required()
def reorder_tasks():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    task_ids = data.get('task_ids', [])

    try:
        for index, task_id in enumerate(task_ids):
            task = Task.query.filter_by(id=task_id, user_id=user_id).first()
            if task:
                task.position = index
        db.session.commit()
        return jsonify({'success': True, 'message': 'Tasks reordered successfully'}), 200
    except Exception as e:
        db.session.rollback()
        logging.error(
            f"Task reordering failed for user {user_id}. Error: {e}", exc_info=True)
        return jsonify({'success': False, 'message': 'An internal server error occurred.'}), 500
