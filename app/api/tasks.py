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
    """Create a new task with enhanced validation and error handling."""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()

        # Enhanced validation
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400

        if not data.get('title') or not data.get('title').strip():
            return jsonify({'success': False, 'message': 'Task title is required and cannot be empty'}), 400

        # Validate project ownership if project_id is provided
        project_id = data.get('project_id')
        if project_id:
            project = Project.query.filter_by(id=project_id, user_id=user_id).first()
            if not project:
                return jsonify({'success': False, 'message': 'Project not found or access denied.'}), 404

        # Validate and parse due_date
        due_date = None
        if data.get('due_date'):
            try:
                # Handle different date formats
                due_date_str = data['due_date']
                if 'Z' in due_date_str:
                    due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
                elif 'T' in due_date_str:
                    due_date = datetime.fromisoformat(due_date_str)
                else:
                    # Assume it's a date string
                    due_date = datetime.fromisoformat(due_date_str + 'T23:59:59')
            except (ValueError, TypeError) as e:
                return jsonify({'success': False, 'message': 'Invalid due date format'}), 400

        # Validate priority
        valid_priorities = ['low', 'medium', 'high']
        priority = data.get('priority', 'medium')
        if priority not in valid_priorities:
            priority = 'medium'

        # Validate status
        valid_statuses = ['todo', 'in-progress', 'completed']
        status = data.get('status', 'todo')
        if status not in valid_statuses:
            status = 'todo'

        # Validate estimated_duration
        estimated_duration = data.get('estimated_duration')
        if estimated_duration is not None:
            try:
                estimated_duration = int(estimated_duration)
                if estimated_duration < 1:
                    return jsonify({'success': False, 'message': 'Estimated duration must be at least 1 minute'}), 400
            except (ValueError, TypeError):
                return jsonify({'success': False, 'message': 'Estimated duration must be a valid number'}), 400

        # Create task
        task = Task(
            title=data['title'].strip(),
            description=data.get('description', '').strip(),
            priority=priority,
            status=status,
            due_date=due_date,
            estimated_duration=estimated_duration,
            user_id=user_id,
            project_id=project_id
        )

        db.session.add(task)
        db.session.commit()

        # Return task data with project info
        project_name = project.name if project else None

        return jsonify({
            'success': True, 
            'message': 'Task created successfully', 
            'data': {
                'task': {
                    'id': task.id,
                    'title': task.title,
                    'description': task.description,
                    'priority': task.priority,
                    'status': task.status,
                    'due_date': task.due_date.isoformat() if task.due_date else None,
                    'estimated_duration': task.estimated_duration,
                    'project_id': task.project_id,
                    'project_name': project_name,
                    'created_at': task.created_at.isoformat() if hasattr(task, 'created_at') and task.created_at else None
                }
            }
        }), 201

    except ValueError as ve:
        logging.error(f"ValueError in task creation: {ve}")
        return jsonify({'success': False, 'message': 'Invalid data provided'}), 400
    except Exception as e:
        db.session.rollback()
        logging.error(f"Task creation failed for user {user_id}. Error: {e}", exc_info=True)
        return jsonify({'success': False, 'message': 'An internal server error occurred.'}), 500

@bp.route('', methods=['GET'])
@jwt_required()
def get_tasks():
    """Get user's tasks with enhanced filtering and sorting options."""
    try:
        user_id = int(get_jwt_identity())

        # Get query parameters for filtering
        project_id = request.args.get('project_id', type=int)
        status = request.args.get('status')
        priority = request.args.get('priority')
        sort_by = request.args.get('sort_by', 'created_at')  # created_at, due_date, priority, title
        sort_order = request.args.get('sort_order', 'desc')  # asc, desc

        # Build query
        query = Task.query.filter_by(user_id=user_id)

        # Apply filters
        if project_id:
            query = query.filter(Task.project_id == project_id)

        if status:
            query = query.filter(Task.status == status)

        if priority:
            query = query.filter(Task.priority == priority)

        # Apply sorting
        if sort_by == 'due_date':
            order_by = Task.due_date.desc() if sort_order == 'desc' else Task.due_date.asc()
        elif sort_by == 'priority':
            # Custom priority ordering: high, medium, low
            priority_order = {'high': 3, 'medium': 2, 'low': 1}
            if sort_order == 'desc':
                order_by = Task.priority.desc()
            else:
                order_by = Task.priority.asc()
        elif sort_by == 'title':
            order_by = Task.title.desc() if sort_order == 'desc' else Task.title.asc()
        else:  # default to created_at
            order_by = Task.created_at.desc() if sort_order == 'desc' else Task.created_at.asc()

        tasks = query.order_by(order_by).all()

        # Format task data with project information
        task_data = []
        for task in tasks:
            project = Project.query.get(task.project_id) if task.project_id else None

            task_data.append({
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'priority': task.priority,
                'status': task.status,
                'due_date': task.due_date.isoformat() if task.due_date else None,
                'estimated_duration': task.estimated_duration,
                'project_id': task.project_id,
                'project_name': project.name if project else None,
                'created_at': task.created_at.isoformat() if hasattr(task, 'created_at') and task.created_at else None,
                'is_overdue': task.due_date < datetime.now() if task.due_date and task.status != 'completed' else False
            })

        return jsonify({
            'success': True, 
            'data': {
                'tasks': task_data,
                'count': len(task_data),
                'filters_applied': {
                    'project_id': project_id,
                    'status': status,
                    'priority': priority,
                    'sort_by': sort_by,
                    'sort_order': sort_order
                }
            }
        }), 200

    except Exception as e:
        logging.error(f"Failed to get tasks for user {user_id}. Error: {e}", exc_info=True)
        return jsonify({'success': False, 'message': 'An internal server error occurred.'}), 500

@bp.route('/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    """Update an existing task with enhanced validation."""
    try:
        user_id = int(get_jwt_identity())
        task = Task.query.filter_by(id=task_id, user_id=user_id).first()

        if not task:
            return jsonify({'success': False, 'message': 'Task not found or access denied.'}), 404

        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400

        # Update simple fields with validation
        if 'title' in data:
            if not data['title'] or not data['title'].strip():
                return jsonify({'success': False, 'message': 'Task title cannot be empty'}), 400
            task.title = data['title'].strip()

        if 'description' in data:
            task.description = data['description'].strip()

        if 'priority' in data:
            if data['priority'] in ['low', 'medium', 'high']:
                task.priority = data['priority']

        if 'status' in data:
            if data['status'] in ['todo', 'in-progress', 'completed']:
                task.status = data['status']

                # Mark completion time if status is completed
                if data['status'] == 'completed' and hasattr(task, 'completed_at'):
                    task.completed_at = datetime.now()

        if 'due_date' in data:
            if data['due_date']:
                try:
                    if 'Z' in data['due_date']:
                        task.due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
                    else:
                        task.due_date = datetime.fromisoformat(data['due_date'])
                except (ValueError, TypeError):
                    return jsonify({'success': False, 'message': 'Invalid due date format'}), 400
            else:
                task.due_date = None

        if 'estimated_duration' in data:
            if data['estimated_duration'] is not None:
                try:
                    duration = int(data['estimated_duration'])
                    if duration < 1:
                        return jsonify({'success': False, 'message': 'Estimated duration must be at least 1 minute'}), 400
                    task.estimated_duration = duration
                except (ValueError, TypeError):
                    return jsonify({'success': False, 'message': 'Invalid estimated duration'}), 400
            else:
                task.estimated_duration = None

        if 'project_id' in data:
            if data['project_id']:
                project = Project.query.filter_by(id=data['project_id'], user_id=user_id).first()
                if not project:
                    return jsonify({'success': False, 'message': 'Project not found or access denied.'}), 404
                task.project_id = data['project_id']
            else:
                task.project_id = None

        db.session.commit()

        # Get updated task data with project info
        project = Project.query.get(task.project_id) if task.project_id else None

        return jsonify({
            'success': True, 
            'message': 'Task updated successfully', 
            'data': {
                'task': {
                    'id': task.id,
                    'title': task.title,
                    'description': task.description,
                    'priority': task.priority,
                    'status': task.status,
                    'due_date': task.due_date.isoformat() if task.due_date else None,
                    'estimated_duration': task.estimated_duration,
                    'project_id': task.project_id,
                    'project_name': project.name if project else None,
                    'created_at': task.created_at.isoformat() if hasattr(task, 'created_at') and task.created_at else None
                }
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        logging.error(f"Task update failed for user {user_id}, task {task_id}. Error: {e}", exc_info=True)
        return jsonify({'success': False, 'message': 'An internal server error occurred.'}), 500

@bp.route('/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    """Delete a task with proper validation."""
    try:
        user_id = int(get_jwt_identity())
        task = Task.query.filter_by(id=task_id, user_id=user_id).first()

        if not task:
            return jsonify({'success': False, 'message': 'Task not found or access denied.'}), 404

        task_title = task.title  # Store for response message

        db.session.delete(task)
        db.session.commit()

        return jsonify({
            'success': True, 
            'message': f'Task "{task_title}" deleted successfully'
        }), 200

    except Exception as e:
        db.session.rollback()
        logging.error(f"Task deletion failed for user {user_id}, task {task_id}. Error: {e}", exc_info=True)
        return jsonify({'success': False, 'message': 'An internal server error occurred.'}), 500

@bp.route('/bulk', methods=['PUT'])
@jwt_required()
def bulk_update_tasks():
    """Bulk update multiple tasks (useful for drag-and-drop reordering or mass status changes)."""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()

        if not data or 'tasks' not in data:
            return jsonify({'success': False, 'message': 'Tasks data required'}), 400

        task_updates = data['tasks']
        updated_count = 0

        for task_update in task_updates:
            task_id = task_update.get('id')
            if not task_id:
                continue

            task = Task.query.filter_by(id=task_id, user_id=user_id).first()
            if not task:
                continue

            # Apply allowed updates
            if 'status' in task_update and task_update['status'] in ['todo', 'in-progress', 'completed']:
                task.status = task_update['status']

            if 'priority' in task_update and task_update['priority'] in ['low', 'medium', 'high']:
                task.priority = task_update['priority']

            if 'project_id' in task_update:
                if task_update['project_id']:
                    project = Project.query.filter_by(id=task_update['project_id'], user_id=user_id).first()
                    if project:
                        task.project_id = task_update['project_id']
                else:
                    task.project_id = None

            updated_count += 1

        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Successfully updated {updated_count} tasks',
            'updated_count': updated_count
        }), 200

    except Exception as e:
        db.session.rollback()
        logging.error(f"Bulk task update failed for user {user_id}. Error: {e}", exc_info=True)
        return jsonify({'success': False, 'message': 'An internal server error occurred.'}), 500

@bp.route('/stats', methods=['GET'])
@jwt_required()
def get_task_stats():
    """Get comprehensive task statistics for the user."""
    try:
        user_id = int(get_jwt_identity())

        tasks = Task.query.filter_by(user_id=user_id).all()

        # Calculate various statistics
        total_tasks = len(tasks)
        completed_tasks = len([t for t in tasks if t.status == 'completed'])
        in_progress_tasks = len([t for t in tasks if t.status == 'in-progress'])
        todo_tasks = total_tasks - completed_tasks - in_progress_tasks

        # Priority breakdown
        high_priority = len([t for t in tasks if t.priority == 'high'])
        medium_priority = len([t for t in tasks if t.priority == 'medium'])
        low_priority = len([t for t in tasks if t.priority == 'low'])

        # Overdue tasks
        overdue_tasks = len([t for t in tasks if t.due_date and t.due_date < datetime.now() and t.status != 'completed'])

        # Due today and this week
        today = datetime.now().date()
        week_from_now = today + timedelta(days=7)

        due_today = len([t for t in tasks if t.due_date and t.due_date.date() == today])
        due_this_week = len([t for t in tasks if t.due_date and today <= t.due_date.date() <= week_from_now])

        # Completion rate
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

        stats = {
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'in_progress_tasks': in_progress_tasks,
            'todo_tasks': todo_tasks,
            'high_priority': high_priority,
            'medium_priority': medium_priority,
            'low_priority': low_priority,
            'overdue_tasks': overdue_tasks,
            'due_today': due_today,
            'due_this_week': due_this_week,
            'completion_rate': round(completion_rate, 1)
        }

        return jsonify({'success': True, 'data': stats}), 200

    except Exception as e:
        logging.error(f"Failed to get task stats for user {user_id}. Error: {e}", exc_info=True)
        return jsonify({'success': False, 'message': 'An internal server error occurred.'}), 500
