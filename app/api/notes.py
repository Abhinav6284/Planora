from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import db
from ..models.note import Note
from ..models.project import Project
from datetime import datetime
import logging

bp = Blueprint('notes', __name__)

@bp.route('', methods=['POST'])
@jwt_required()
def create_note():
    """Create a new note with optional project association."""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()

        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400

        if not data.get('title') or not data.get('title').strip():
            return jsonify({'success': False, 'message': 'Note title is required'}), 400

        if not data.get('content') or not data.get('content').strip():
            return jsonify({'success': False, 'message': 'Note content is required'}), 400

        # Validate project if provided
        project_id = data.get('project_id')
        project = None
        if project_id:
            project = Project.query.filter_by(id=project_id, user_id=user_id).first()
            if not project:
                return jsonify({'success': False, 'message': 'Project not found or access denied'}), 404

        # Create note
        note = Note(
            title=data['title'].strip(),
            content=data['content'].strip(),
            project_id=project_id,
            user_id=user_id
        )

        db.session.add(note)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Note created successfully',
            'data': {
                'note': {
                    'id': note.id,
                    'title': note.title,
                    'content': note.content,
                    'project_id': note.project_id,
                    'project_name': project.name if project else None,
                    'created_at': note.created_at.isoformat() if hasattr(note, 'created_at') and note.created_at else None,
                    'updated_at': note.updated_at.isoformat() if hasattr(note, 'updated_at') and note.updated_at else None
                }
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        logging.error(f"Note creation failed for user {user_id}. Error: {e}", exc_info=True)
        return jsonify({'success': False, 'message': 'An internal server error occurred.'}), 500

@bp.route('', methods=['GET'])
@jwt_required()
def get_notes():
    """Get user's notes with optional project filtering."""
    try:
        user_id = int(get_jwt_identity())

        # Get query parameters
        project_id = request.args.get('project_id', type=int)
        search = request.args.get('search', '').strip()
        sort_by = request.args.get('sort_by', 'updated_at')  # created_at, updated_at, title
        sort_order = request.args.get('sort_order', 'desc')  # asc, desc

        # Build query
        query = Note.query.filter_by(user_id=user_id)

        # Apply filters
        if project_id:
            query = query.filter(Note.project_id == project_id)

        if search:
            search_term = f"%{search}%"
            query = query.filter(
                db.or_(
                    Note.title.ilike(search_term),
                    Note.content.ilike(search_term)
                )
            )

        # Apply sorting
        if sort_by == 'created_at':
            order_by = Note.created_at.desc() if sort_order == 'desc' else Note.created_at.asc()
        elif sort_by == 'title':
            order_by = Note.title.desc() if sort_order == 'desc' else Note.title.asc()
        else:  # default to updated_at
            order_by = Note.updated_at.desc() if sort_order == 'desc' else Note.updated_at.asc()

        notes = query.order_by(order_by).all()

        # Format note data with project information
        note_data = []
        for note in notes:
            project = Project.query.get(note.project_id) if note.project_id else None

            note_data.append({
                'id': note.id,
                'title': note.title,
                'content': note.content,
                'project_id': note.project_id,
                'project_name': project.name if project else None,
                'created_at': note.created_at.isoformat() if hasattr(note, 'created_at') and note.created_at else None,
                'updated_at': note.updated_at.isoformat() if hasattr(note, 'updated_at') and note.updated_at else None,
                'word_count': len(note.content.split()) if note.content else 0
            })

        return jsonify({
            'success': True,
            'data': {
                'notes': note_data,
                'count': len(note_data),
                'filters_applied': {
                    'project_id': project_id,
                    'search': search,
                    'sort_by': sort_by,
                    'sort_order': sort_order
                }
            }
        }), 200

    except Exception as e:
        logging.error(f"Failed to get notes for user {user_id}. Error: {e}", exc_info=True)
        return jsonify({'success': False, 'message': 'An internal server error occurred.'}), 500

@bp.route('/<int:note_id>', methods=['GET'])
@jwt_required()
def get_note(note_id):
    """Get a specific note by ID."""
    try:
        user_id = int(get_jwt_identity())
        note = Note.query.filter_by(id=note_id, user_id=user_id).first()

        if not note:
            return jsonify({'success': False, 'message': 'Note not found or access denied'}), 404

        project = Project.query.get(note.project_id) if note.project_id else None

        return jsonify({
            'success': True,
            'data': {
                'note': {
                    'id': note.id,
                    'title': note.title,
                    'content': note.content,
                    'project_id': note.project_id,
                    'project_name': project.name if project else None,
                    'created_at': note.created_at.isoformat() if hasattr(note, 'created_at') and note.created_at else None,
                    'updated_at': note.updated_at.isoformat() if hasattr(note, 'updated_at') and note.updated_at else None,
                    'word_count': len(note.content.split()) if note.content else 0
                }
            }
        }), 200

    except Exception as e:
        logging.error(f"Failed to get note {note_id} for user {user_id}. Error: {e}", exc_info=True)
        return jsonify({'success': False, 'message': 'An internal server error occurred.'}), 500

@bp.route('/<int:note_id>', methods=['PUT'])
@jwt_required()
def update_note(note_id):
    """Update an existing note."""
    try:
        user_id = int(get_jwt_identity())
        note = Note.query.filter_by(id=note_id, user_id=user_id).first()

        if not note:
            return jsonify({'success': False, 'message': 'Note not found or access denied'}), 404

        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400

        # Update fields
        if 'title' in data:
            if not data['title'] or not data['title'].strip():
                return jsonify({'success': False, 'message': 'Note title cannot be empty'}), 400
            note.title = data['title'].strip()

        if 'content' in data:
            if not data['content'] or not data['content'].strip():
                return jsonify({'success': False, 'message': 'Note content cannot be empty'}), 400
            note.content = data['content'].strip()

        if 'project_id' in data:
            if data['project_id']:
                project = Project.query.filter_by(id=data['project_id'], user_id=user_id).first()
                if not project:
                    return jsonify({'success': False, 'message': 'Project not found or access denied'}), 404
                note.project_id = data['project_id']
            else:
                note.project_id = None

        # Update timestamp
        if hasattr(note, 'updated_at'):
            note.updated_at = datetime.now()

        db.session.commit()

        # Get updated note data with project info
        project = Project.query.get(note.project_id) if note.project_id else None

        return jsonify({
            'success': True,
            'message': 'Note updated successfully',
            'data': {
                'note': {
                    'id': note.id,
                    'title': note.title,
                    'content': note.content,
                    'project_id': note.project_id,
                    'project_name': project.name if project else None,
                    'created_at': note.created_at.isoformat() if hasattr(note, 'created_at') and note.created_at else None,
                    'updated_at': note.updated_at.isoformat() if hasattr(note, 'updated_at') and note.updated_at else None,
                    'word_count': len(note.content.split()) if note.content else 0
                }
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        logging.error(f"Note update failed for user {user_id}, note {note_id}. Error: {e}", exc_info=True)
        return jsonify({'success': False, 'message': 'An internal server error occurred.'}), 500

@bp.route('/<int:note_id>', methods=['DELETE'])
@jwt_required()
def delete_note(note_id):
    """Delete a note."""
    try:
        user_id = int(get_jwt_identity())
        note = Note.query.filter_by(id=note_id, user_id=user_id).first()

        if not note:
            return jsonify({'success': False, 'message': 'Note not found or access denied'}), 404

        note_title = note.title  # Store for response message

        db.session.delete(note)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Note "{note_title}" deleted successfully'
        }), 200

    except Exception as e:
        db.session.rollback()
        logging.error(f"Note deletion failed for user {user_id}, note {note_id}. Error: {e}", exc_info=True)
        return jsonify({'success': False, 'message': 'An internal server error occurred.'}), 500

@bp.route('/search', methods=['GET'])
@jwt_required()
def search_notes():
    """Advanced search functionality for notes."""
    try:
        user_id = int(get_jwt_identity())

        # Get search parameters
        query_text = request.args.get('q', '').strip()
        project_id = request.args.get('project_id', type=int)
        created_after = request.args.get('created_after')
        created_before = request.args.get('created_before')

        if not query_text:
            return jsonify({'success': False, 'message': 'Search query is required'}), 400

        # Build search query
        search_query = Note.query.filter_by(user_id=user_id)

        # Text search
        search_term = f"%{query_text}%"
        search_query = search_query.filter(
            db.or_(
                Note.title.ilike(search_term),
                Note.content.ilike(search_term)
            )
        )

        # Project filter
        if project_id:
            search_query = search_query.filter(Note.project_id == project_id)

        # Date filters
        if created_after:
            try:
                after_date = datetime.fromisoformat(created_after)
                search_query = search_query.filter(Note.created_at >= after_date)
            except ValueError:
                return jsonify({'success': False, 'message': 'Invalid created_after date format'}), 400

        if created_before:
            try:
                before_date = datetime.fromisoformat(created_before)
                search_query = search_query.filter(Note.created_at <= before_date)
            except ValueError:
                return jsonify({'success': False, 'message': 'Invalid created_before date format'}), 400

        # Execute search
        notes = search_query.order_by(Note.updated_at.desc()).all()

        # Format results with highlighting (basic)
        results = []
        for note in notes:
            project = Project.query.get(note.project_id) if note.project_id else None

            # Simple highlighting - replace with proper highlighting library in production
            highlighted_title = note.title.replace(query_text, f"<mark>{query_text}</mark>") if query_text.lower() in note.title.lower() else note.title
            highlighted_content = note.content[:200] + "..." if len(note.content) > 200 else note.content
            if query_text.lower() in highlighted_content.lower():
                highlighted_content = highlighted_content.replace(query_text, f"<mark>{query_text}</mark>")

            results.append({
                'id': note.id,
                'title': note.title,
                'highlighted_title': highlighted_title,
                'content_preview': highlighted_content,
                'project_id': note.project_id,
                'project_name': project.name if project else None,
                'created_at': note.created_at.isoformat() if hasattr(note, 'created_at') and note.created_at else None,
                'updated_at': note.updated_at.isoformat() if hasattr(note, 'updated_at') and note.updated_at else None
            })

        return jsonify({
            'success': True,
            'data': {
                'results': results,
                'count': len(results),
                'query': query_text,
                'search_parameters': {
                    'project_id': project_id,
                    'created_after': created_after,
                    'created_before': created_before
                }
            }
        }), 200

    except Exception as e:
        logging.error(f"Note search failed for user {user_id}. Error: {e}", exc_info=True)
        return jsonify({'success': False, 'message': 'An internal server error occurred.'}), 500
