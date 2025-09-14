# planora/app/api/roadmap.py

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import db
from ..models.project import Project
from ..models.task import Task
# We will reuse the AI project generator
from .ai import generate_project_from_goal
import google.generativeai as genai
import os
import json

bp = Blueprint('roadmap', __name__)

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))


@bp.route('/data', methods=['GET'])
@jwt_required()
def roadmap_data():
    # ... (this function remains the same as before)
    try:
        user_id = int(get_jwt_identity())
        projects = Project.query.filter_by(user_id=user_id).order_by(
            Project.created_at.desc()).all()

        projects_data = []
        for project in projects:
            project_dict = {
                'id': project.id,
                'name': project.name,
                'description': project.description,
                'status': project.status,
                'tasks': [task.to_dict() for task in project.tasks.order_by(task.due_date.asc())]
            }
            projects_data.append(project_dict)

        return jsonify({'success': True, 'data': {'projects': projects_data}}), 200

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@bp.route('/chat', methods=['POST'])
@jwt_required()
def project_chat_agent():
    """
    Handles AI chat conversations, determines user intent, and performs actions.
    """
    data = request.get_json()
    user_id = int(get_jwt_identity())
    # Can be null if creating a new project
    project_id = data.get('project_id')
    user_message = data.get('message')

    if not user_message:
        return jsonify({'success': False, 'message': 'Message is required.'}), 400

    # --- Build the Context for the AI ---
    project_context = "No specific project is currently selected."
    if project_id:
        project = Project.query.filter_by(
            id=project_id, user_id=user_id).first()
        if project:
            tasks_context = "\n".join(
                [f"- Task ID {task.id}: '{task.title}' (Status: {task.status})" for task in project.tasks]
            )
            project_context = f"""
            The user is currently focused on the following project:
            Project ID: {project.id}
            Project Name: {project.name}
            Project Description: {project.description}
            Tasks in this project:\n{tasks_context}
            """

    # --- Prompt Engineering with Function Calling ---
    prompt = f"""You are 'Planora Agent', an AI that helps users manage their projects.
    Your task is to analyze the user's message and the current project context, then decide on one of three actions: 'answer', 'create_project', or 'add_task'.
    You MUST respond with a single, clean JSON object and nothing else.

    --- CONTEXT ---
    {project_context}
    --- END CONTEXT ---

    User's Message: "{user_message}"

    --- INSTRUCTIONS ---
    1.  If the user is asking a question about the current project, choose the 'answer' action. Provide a helpful text response.
    2.  If the user wants to create a brand NEW project (e.g., "make a new project for...", "generate a plan for..."), choose the 'create_project' action. The 'goal' should be the user's stated objective.
    3.  If the user wants to add a new task to the CURRENTLY selected project (e.g., "add a task to...", "we need to do X"), choose the 'add_task' action. The 'title' should be the task's name.

    Choose one of the following JSON formats for your response:
    - For answering questions: {{"action": "answer", "response": "Your helpful answer here."}}
    - For creating a new project: {{"action": "create_project", "goal": "The user's goal for the new project."}}
    - For adding a task to the current project: {{"action": "add_task", "title": "The title of the new task."}}
    """

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)

        # Clean up the response to ensure it's valid JSON
        cleaned_response = response.text.strip().replace('```json', '').replace('```', '')
        action_plan = json.loads(cleaned_response)

        action = action_plan.get('action')

        if action == 'answer':
            return jsonify({'success': True, 'reply': action_plan.get('response'), 'action_taken': 'none'})

        elif action == 'create_project':
            # This is a placeholder for the more complex project generation logic.
            # In a real app, you would call your existing AI project generation function here.
            new_project = Project(
                name=f"New Project: {action_plan.get('goal')}", user_id=user_id)
            db.session.add(new_project)
            db.session.commit()
            return jsonify({'success': True, 'reply': f"I have created a new project for you: '{new_project.name}'. I recommend using the 'Generate with AI' button for a full plan.", 'action_taken': 'reload'})

        elif action == 'add_task':
            if not project_id:
                return jsonify({'success': True, 'reply': "Please select a project first before adding a task.", 'action_taken': 'none'})

            new_task = Task(title=action_plan.get('title'), user_id=user_id)
            project = Project.query.get(project_id)
            project.tasks.append(new_task)
            db.session.commit()
            return jsonify({'success': True, 'reply': f"OK, I've added the task '{new_task.title}' to the '{project.name}' project.", 'action_taken': 'reload'})

        else:
            return jsonify({'success': True, 'reply': "I'm not sure how to handle that, but I'm learning!", 'action_taken': 'none'})

    except Exception as e:
        return jsonify({'success': False, 'message': f'An error occurred: {str(e)}'}), 500
