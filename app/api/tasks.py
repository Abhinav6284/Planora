from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import desc, asc
from datetime import datetime
from ..extensions import db
from ..models.task import Task
from ..models.user import User
from ..models.category import Category
from ..models.focus_session import FocusSession

bp = Blueprint('tasks', __name__)


@bp.route('', methods=['GET'])
@jwt_required()
def get_tasks():
    """Get user's tasks with filtering and pagination"""
    try:
        user_id = int(get_jwt_identity())

        # Query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        status = request.args.get('status')
        priority = request.args.get('priority')
        category_id = request.args.get('category_id', type=int)
        search = request.args.get('search')
        sort_by = request.args.get('sort_by', 'created_at')
        order = request.args.get('order', 'desc')

        # Build query
        query = Task.query.filter_by(user_id=user_id)

        # Apply filters
        if status:
            query = query.filter_by(status=status)
        if priority:
            query = query.filter_by(priority=priority)
        if category_id:
            query = query.filter_by(category_id=category_id)
        if search:
            query = query.filter(Task.title.contains(search))

        # Apply sorting
        if hasattr(Task, sort_by):
            if order == 'desc':
                query = query.order_by(desc(getattr(Task, sort_by)))
            else:
                query = query.order_by(asc(getattr(Task, sort_by)))

        # Paginate
        tasks = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        return jsonify({
            'success': True,
            'data': {
                'tasks': [task.to_dict() for task in tasks.items],
                'pagination': {
                    'page': page,
                    'pages': tasks.pages,
                    'per_page': per_page,
                    'total': tasks.total,
                    'has_next': tasks.has_next,
                    'has_prev': tasks.has_prev
                }
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to get tasks',
            'error': str(e)
        }), 500


@bp.route('', methods=['POST'])
@jwt_required()
def create_task():
    """Create a new task"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        if not data or not data.get('title'):
            return jsonify({
                'success': False,
                'message': 'Task title is required'
            }), 400

        # Create task
        task = Task(
            title=data['title'],
            description=data.get('description'),
            priority=data.get('priority', 'medium'),
            status=data.get('status', 'todo'),
            estimated_duration=data.get('estimated_duration'),
            category_id=data.get('category_id'),
            user_id=user_id
        )

        # Parse due_date if provided
        if data.get('due_date'):
            try:
                task.due_date = datetime.fromisoformat(data['due_date'])
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': 'Invalid due_date format. Use ISO format: YYYY-MM-DDTHH:MM:SS'
                }), 400

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


@bp.route('/<int:task_id>', methods=['GET'])
@jwt_required()
def get_task(task_id):
    """Get a specific task"""
    try:
        user_id = get_jwt_identity()
        task = Task.query.filter_by(id=task_id, user_id=user_id).first()

        if not task:
            return jsonify({
                'success': False,
                'message': 'Task not found'
            }), 404

        return jsonify({
            'success': True,
            'data': {
                'task': task.to_dict(include_subtasks=True)
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to get task',
            'error': str(e)
        }), 500


@bp.route('/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    """Update a task"""
    try:
        user_id = get_jwt_identity()
        task = Task.query.filter_by(id=task_id, user_id=user_id).first()

        if not task:
            return jsonify({
                'success': False,
                'message': 'Task not found'
            }), 404

        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400

        # Update fields
        if 'title' in data:
            task.title = data['title']
        if 'description' in data:
            task.description = data['description']
        if 'priority' in data:
            task.priority = data['priority']
        if 'status' in data:
            task.status = data['status']
            # Mark completed if status is completed
            if data['status'] == 'completed' and not task.completed_at:
                task.mark_completed()
        if 'estimated_duration' in data:
            task.estimated_duration = data['estimated_duration']
        if 'category_id' in data:
            task.category_id = data['category_id']
        if 'due_date' in data:
            if data['due_date']:
                try:
                    task.due_date = datetime.fromisoformat(data['due_date'])
                except ValueError:
                    return jsonify({
                        'success': False,
                        'message': 'Invalid due_date format'
                    }), 400
            else:
                task.due_date = None

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Task updated successfully',
            'data': {
                'task': task.to_dict()
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Failed to update task',
            'error': str(e)
        }), 500


@bp.route('/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    """Delete a task"""
    try:
        user_id = get_jwt_identity()
        task = Task.query.filter_by(id=task_id, user_id=user_id).first()

        if not task:
            return jsonify({
                'success': False,
                'message': 'Task not found'
            }), 404

        db.session.delete(task)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Task deleted successfully'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Failed to delete task',
            'error': str(e)
        }), 500
