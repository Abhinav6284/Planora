from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import db
from ..models.category import Category
import logging

bp = Blueprint('categories', __name__)


@bp.route('', methods=['GET'])
@jwt_required()
def get_categories():
    """Get all of the user's categories."""
    try:
        user_id = int(get_jwt_identity())
        categories = Category.query.filter_by(
            user_id=user_id).order_by(Category.name.asc()).all()
        category_data = [{'id': c.id, 'name': c.name,
                          'color': c.color} for c in categories]
        return jsonify({'success': True, 'data': {'categories': category_data}}), 200
    except Exception as e:
        logging.error(
            f"Failed to get categories for user {get_jwt_identity()}. Error: {e}", exc_info=True)
        return jsonify({'success': False, 'message': 'An internal server error occurred.'}), 500


@bp.route('', methods=['POST'])
@jwt_required()
def create_category():
    """Create a new category."""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()

        if not data or not data.get('name'):
            return jsonify({'success': False, 'message': 'Category name is required'}), 400

        category = Category(
            name=data['name'],
            description=data.get('description', ''),
            color=data.get('color', '#3B82F6'),
            user_id=user_id
        )
        db.session.add(category)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Category created successfully',
            'data': {'id': category.id, 'name': category.name, 'color': category.color}
        }), 201

    except Exception as e:
        db.session.rollback()
        logging.error(
            f"Category creation failed for user {get_jwt_identity()}. Error: {e}", exc_info=True)
        return jsonify({'success': False, 'message': 'An internal server error occurred.'}), 500


@bp.route('/<int:category_id>', methods=['PUT'])
@jwt_required()
def update_category(category_id):
    """Update an existing category."""
    try:
        user_id = int(get_jwt_identity())
        category = Category.query.filter_by(
            id=category_id, user_id=user_id).first_or_404()
        data = request.get_json()

        category.name = data.get('name', category.name)
        category.description = data.get('description', category.description)
        category.color = data.get('color', category.color)

        db.session.commit()
        return jsonify({'success': True, 'message': 'Category updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        logging.error(
            f"Category update failed for user {get_jwt_identity()}. Error: {e}", exc_info=True)
        return jsonify({'success': False, 'message': 'An internal server error occurred.'}), 500


@bp.route('/<int:category_id>', methods=['DELETE'])
@jwt_required()
def delete_category(category_id):
    """Delete a category."""
    try:
        user_id = int(get_jwt_identity())
        category = Category.query.filter_by(
            id=category_id, user_id=user_id).first_or_404()

        db.session.delete(category)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Category deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        logging.error(
            f"Category deletion failed for user {get_jwt_identity()}. Error: {e}", exc_info=True)
        return jsonify({'success': False, 'message': 'An internal server error occurred.'}), 500
