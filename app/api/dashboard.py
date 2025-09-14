from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import db
from ..models.user import User
from ..models.task import Task
from ..models.project import Project
import logging
from datetime import datetime, date, timedelta

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

        # Use the session explicitly for all queries
        user = db.session.get(User, user_id)
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404

        # --- Data Fetching ---
        projects = db.session.query(Project).filter_by(user_id=user_id, status='active').order_by(
            Project.created_at.desc()).all()

        tasks = db.session.query(Task).filter_by(
            user_id=user_id).order_by(Task.due_date.asc()).all()

        # --- Data Preparation ---
        project_data = [{'id': p.id, 'name': p.name,
                         'description': p.description} for p in projects]
        task_data = [{'id': t.id, 'title': t.title, 'status': t.status,
                      'due_date': t.due_date.isoformat() if t.due_date else None,
                      # Safely get project_id
                      'project_id': t.projects[0].id if t.projects else None,
                      'estimated_duration': t.estimated_duration} for t in tasks]
        calendar_task_data = [{'id': t.id, 'title': t.title,
                               'start': t.due_date.isoformat()} for t in tasks if t.due_date]

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
        db.session.rollback()  # Ensure session is rolled back on error
        logging.error(
            f"Failed to fetch dashboard data for user_id {get_jwt_identity()}. Error: {e}", exc_info=True)
        return jsonify({'success': False, 'message': 'An internal server error occurred.'}), 500
