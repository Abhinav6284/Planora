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

# We will add POST, PUT, DELETE for categories later
