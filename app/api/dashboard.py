from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.user import User
from ..models.task import Task
from ..models.project import Project
import logging
from datetime import datetime, date, timedelta  # <-- THE FIX IS HERE

bp = Blueprint('dashboard', __name__)


@bp.route('/data', methods=['GET'])
@jwt_required()
def dashboard_data():
    """
    Fetches and returns all necessary data for the user's dashboard,
    including specific data for the overview and calendar sections.
    """
    try:
        user_id_str = get_jwt_identity()
        user_id = int(user_id_str)

        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404

        # --- Data Fetching ---
        projects = Project.query.filter_by(user_id=user_id, status='active').order_by(
            Project.created_at.desc()).all()

        tasks = Task.query.filter_by(user_id=user_id).filter(
            Task.status != 'completed').order_by(Task.due_date.asc()).all()

        today = date.today()
        start_of_month = today.replace(day=1)
        # To get the end of the month, we find the first day of the next month
        # and subtract one day. This is a robust way to handle months with different numbers of days.
        next_month_start = (start_of_month.replace(
            day=28) + timedelta(days=4)).replace(day=1)

        calendar_tasks = Task.query.filter(
            Task.user_id == user_id,
            Task.due_date >= start_of_month,
            Task.due_date < next_month_start
        ).all()

        # --- Data Preparation ---
        project_data = [{'id': p.id, 'name': p.name,
                         'description': p.description} for p in projects]
        task_data = [{'id': t.id, 'title': t.title, 'status': t.status,
                      'due_date': t.due_date.isoformat() if t.due_date else None} for t in tasks]
        calendar_task_data = [{'id': t.id, 'title': t.title,
                               'due_date': t.due_date.isoformat()} for t in calendar_tasks]

        return jsonify({
            'success': True,
            'data': {
                'user': user.to_dict(include_sensitive=True),
                'stats': user.get_task_stats(),
                'projects': project_data,
                'tasks': task_data,
                'calendar_tasks': calendar_task_data
            }
        }), 200

    except Exception as e:
        logging.error(
            f"Failed to fetch dashboard data for user_id {get_jwt_identity()}. Error: {e}", exc_info=True)
        return jsonify({'success': False, 'message': 'An internal server error occurred.'}), 500
