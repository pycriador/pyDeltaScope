"""
Public API documentation route
"""
from flask import Blueprint, render_template

api_docs_bp = Blueprint('api_docs', __name__)


@api_docs_bp.route('/api-docs')
def api_documentation():
    """Public API documentation page"""
    return render_template('api_docs.html')

