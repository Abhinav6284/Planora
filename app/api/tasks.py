from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from ..extensions import db

# Create blueprint
bp = Blueprint('tasks', __name__)


@bp.route('', methods=['POST'])
@jwt_required()
def create_task():
    """Create a new task"""
    from ..models.task import Task

    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()

        if not data or not data.get('title'):
            return jsonify({
                'success': False,
                'message': 'Task title is required'
            }), 400

        task = Task(
            title=data['title'],
            description=data.get('description', ''),
            priority=data.get('priority', 'medium'),
            estimated_duration=data.get('estimated_duration'),
            user_id=user_id
        )

        db.session.add(task)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Task created successfully',
            'data': {
                'task': task.to_dict()
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Failed to create task',
            'error': str(e)
        }), 500


@bp.route('', methods=['GET'])
@jwt_required()
def get_tasks():
    """Get user's tasks"""
    from ..models.task import Task

    try:
        user_id = int(get_jwt_identity())
        tasks = Task.query.filter_by(user_id=user_id).order_by(Task.created_at.desc()).all()

        return jsonify({
            'success': True,
            'data': {
                'tasks': [task.to_dict() for task in tasks],
                'total': len(tasks)
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to get tasks',
            'error': str(e)
        }), 500


@bp.route('/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    """Update a task"""
    from ..models.task import Task

    try:
        user_id = int(get_jwt_identity())
        task = Task.query.filter_by(id=task_id, user_id=user_id).first()

        if not task:
            return jsonify({'success': False, 'message': 'Task not found'}), 404

        data = request.get_json()

        if 'title' in data:
            task.title = data['title']
        if 'description' in data:
            task.description = data['description']
        if 'priority' in data:
            task.priority = data['priority']
        if 'status' in data:
            task.status = data['status']
            if data['status'] == 'completed':
                task.mark_completed()

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Task updated successfully',
            'data': {'task': task.to_dict()}
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    """Delete a task"""
    from ..models.task import Task

    try:
        user_id = int(get_jwt_identity())
        task = Task.query.filter_by(id=task_id, user_id=user_id).first()

        if not task:
            return jsonify({'success': False, 'message': 'Task not found'}), 404

        db.session.delete(task)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Task deleted successfully'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
