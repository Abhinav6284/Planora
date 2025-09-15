# CORRECTED VERSION OF ai.py
import os
import json
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import db
from ..models.project import Project
from ..models.task import Task
from datetime import datetime, timedelta
import logging
import google.generativeai as genai

bp = Blueprint('ai', __name__)

# Configure the Gemini API
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))


@bp.route('/generate-project', methods=['POST'])
@jwt_required()
def generate_project_from_goal():
    """
    Generates a project and tasks from a user's goal using AI.
    """
    user_id = int(get_jwt_identity())
    data = request.get_json()
    goal = data.get('goal')

    if not goal:
        return jsonify({'success': False, 'message': 'Goal is required'}), 400

    try:
        # --- This is the core of the AI integration ---
        model = genai.GenerativeModel('gemini-1.5-flash')

        # This prompt is crucial. It tells the AI exactly what format to return.
        prompt = """You are an expert mentor and project planner. Your job is to create a structured project roadmap for the user's goal.

The roadmap should be actionable, realistic, and designed to guide the user step by step like a mentor would.

The user's goal is: "{goal}"

Please return the response strictly in clean JSON format. Do not include any extra text outside the JSON block.

The JSON must follow this structure:

{{
  "project_name": "A concise and professional name for the project",
  "project_description": "A brief, one-paragraph summary of the project and its significance",
  "mini_projects": [
    {{
      "title": "A well-thought-out mini project name",
      "description": "A short description of what this mini project covers and why it's important",
      "tasks": [
        {{
          "title": "A clear, actionable task title",
          "description": "A detailed description of what needs to be done",
          "day": 1,
          "estimated_duration_minutes": 90,
          "resources": [
            {{
              "name": "Resource name",
              "link": "https://..."
            }}
          ]
        }}
      ]
    }}
  ],
  "major_projects": [
    {{
      "title": "A professional major project name",
      "description": "One-paragraph explanation of what this project involves and what it demonstrates",
      "tasks": [
        {{
          "title": "A clear, mentor-style task title",
          "description": "A detailed explanation of the task with actionable steps",
          "day": 20,
          "estimated_duration_minutes": 180,
          "resources": [
            {{
              "name": "Documentation or guide",
              "link": "https://..."
            }},
            {{
              "name": "Video tutorial",
              "link": "https://..."
            }}
          ]
        }}
      ]
    }}
  ]
}}

Guidelines:
- Break the roadmap into **mini-projects** (stepping stones for practice) and **major projects** (capstone-style projects).
- Provide **realistic daily tasks** with estimated time in minutes.
- Always include at least one **relevant resource link** (documentation, GitHub repo, or video) for each task.
- Ensure that the roadmap feels like **professional mentorship** — logical progression, building from basics to advanced.
""".format(goal=goal)

        response = model.generate_content(prompt)

        # Clean up the response to ensure it's valid JSON
        cleaned_response = response.text.strip().replace('```json', '').replace('```', '')
        plan = json.loads(cleaned_response)

        # FIXED: Added missing closing parenthesis
        new_project = Project(
            name=plan['project_name'],
            description=plan['project_description'],
            user_id=user_id
        )

        # FIXED: Added missing closing parenthesis
        db.session.add(new_project)
        db.session.flush()  # Use flush to get the new_project.id before committing

        # Create the tasks from both mini and major projects
        today = datetime.utcnow().date()
        all_tasks = []

        if 'mini_projects' in plan:
            for mini_project in plan['mini_projects']:
                all_tasks.extend(mini_project.get('tasks', []))

        if 'major_projects' in plan:
            for major_project in plan['major_projects']:
                all_tasks.extend(major_project.get('tasks', []))

        for task_data in all_tasks:
            due_date = today + timedelta(days=task_data.get('day', 1) - 1)

            # FIXED: Added missing closing parenthesis
            new_task = Task(
                title=task_data.get('title'),
                description=task_data.get('description', ''),
                user_id=user_id,
                due_date=datetime.combine(due_date, datetime.min.time()),
                status='todo',
                estimated_duration=task_data.get('estimated_duration_minutes')
            )

            # FIXED: Added missing closing parentheses
            new_task.projects.append(new_project)
            db.session.add(new_task)

        db.session.commit()

        return jsonify({'success': True, 'message': 'AI-powered project created successfully!'}), 201

    except Exception as e:
        db.session.rollback()
        logging.error(
            f"AI project generation failed for user {user_id}. Error: {e}", exc_info=True)
        return jsonify({'success': False, 'message': f'An internal server error occurred: {e}'}), 500
