from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import db
from ..models.user import User
from ..models.task import Task
from ..models.project import Project
import logging
from datetime import datetime, date, timedelta
from sqlalchemy import func

bp = Blueprint('dashboard', __name__)

@bp.route('/data', methods=['GET'])
@jwt_required()
def dashboard_data():
    """
    Fetches and returns all necessary data for the user's dashboard,
    including comprehensive statistics and data for all dashboard sections.
    """
    try:
        user_id_str = get_jwt_identity()
        user_id = int(user_id_str)

        # Get user with error handling
        user = db.session.get(User, user_id)
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404

        # Fetch data with optimized queries
        projects = db.session.query(Project).filter_by(
            user_id=user_id, 
            status='active'
        ).order_by(Project.created_at.desc()).all()

        tasks = db.session.query(Task).filter_by(
            user_id=user_id
        ).order_by(Task.due_date.asc()).all()

        # Calculate comprehensive statistics
        total_tasks = len(tasks)
        completed_tasks = len([t for t in tasks if t.status == 'completed'])
        in_progress_tasks = len([t for t in tasks if t.status == 'in-progress'])
        overdue_tasks = len([t for t in tasks if t.due_date and t.due_date < datetime.now() and t.status != 'completed'])

        # Calculate productivity metrics
        today_tasks = [t for t in tasks if t.due_date and t.due_date.date() == date.today()]
        this_week_completed = len([t for t in tasks if t.completed_at and t.completed_at >= datetime.now() - timedelta(days=7)])

        # Prepare data with enhanced structure
        project_data = []
        for p in projects:
            project_tasks = [t for t in tasks if t.project_id == p.id]
            project_completed = len([t for t in project_tasks if t.status == 'completed'])
            progress = int((project_completed / len(project_tasks)) * 100) if project_tasks else 0

            project_data.append({
                'id': p.id,
                'name': p.name,
                'description': p.description,
                'status': p.status,
                'progress': progress,
                'task_count': len(project_tasks),
                'created_at': p.created_at.isoformat() if p.created_at else None
            })

        task_data = []
        for t in tasks:
            task_data.append({
                'id': t.id,
                'title': t.title,
                'description': t.description,
                'status': t.status,
                'priority': t.priority,
                'due_date': t.due_date.isoformat() if t.due_date else None,
                'project_id': t.project_id,
                'estimated_duration': t.estimated_duration,
                'created_at': t.created_at.isoformat() if t.created_at else None,
                'completed_at': t.completed_at.isoformat() if hasattr(t, 'completed_at') and t.completed_at else None
            })

        # Calendar events for FullCalendar
        calendar_task_data = []
        for t in tasks:
            if t.due_date:
                calendar_task_data.append({
                    'id': f'task_{t.id}',
                    'title': t.title,
                    'start': t.due_date.isoformat(),
                    'backgroundColor': '#00d4ff' if t.status != 'completed' else '#2ea043',
                    'borderColor': '#00d4ff' if t.status != 'completed' else '#2ea043'
                })

        # Enhanced statistics
        stats = {
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'in_progress_tasks': in_progress_tasks,
            'todo_tasks': total_tasks - completed_tasks - in_progress_tasks,
            'overdue_tasks': overdue_tasks,
            'today_tasks': len(today_tasks),
            'this_week_completed': this_week_completed,
            'completion_rate': int((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0,
            'total_projects': len(projects)
        }

        return jsonify({
            'success': True,
            'data': {
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email if hasattr(user, 'email') else None
                },
                'stats': stats,
                'projects': project_data,
                'tasks': task_data,
                'calendar_tasks': calendar_task_data,
                'last_updated': datetime.now().isoformat()
            }
        }), 200

    except ValueError as ve:
        logging.error(f"Invalid user_id format: {user_id_str}. Error: {ve}")
        return jsonify({'success': False, 'message': 'Invalid user ID format.'}), 400
    except Exception as e:
        db.session.rollback()
        logging.error(f"Failed to fetch dashboard data for user_id {get_jwt_identity()}. Error: {e}", exc_info=True)
        return jsonify({'success': False, 'message': 'An internal server error occurred.'}), 500

@bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    """Get detailed statistics for analytics dashboard"""
    try:
        user_id = int(get_jwt_identity())

        # Get task statistics by date for charts
        task_stats = db.session.query(
            func.date(Task.created_at).label('date'),
            func.count(Task.id).label('count'),
            Task.status
        ).filter_by(user_id=user_id).group_by(
            func.date(Task.created_at), Task.status
        ).all()

        # Get project statistics
        project_stats = db.session.query(
            func.date(Project.created_at).label('date'),
            func.count(Project.id).label('count')
        ).filter_by(user_id=user_id).group_by(
            func.date(Project.created_at)
        ).all()

        # Format data for charts
        chart_data = {
            'tasks_by_date': [{'date': str(stat.date), 'count': stat.count, 'status': stat.status} for stat in task_stats],
            'projects_by_date': [{'date': str(stat.date), 'count': stat.count} for stat in project_stats]
        }

        return jsonify({'success': True, 'data': chart_data}), 200

    except Exception as e:
        logging.error(f"Failed to fetch stats for user {get_jwt_identity()}. Error: {e}", exc_info=True)
        return jsonify({'success': False, 'message': 'Failed to fetch statistics'}), 500
