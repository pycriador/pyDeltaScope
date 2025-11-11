from flask import Blueprint, render_template
from app.models.database_connection import DatabaseConnection
from app.utils.security import login_required_template

tables_template_bp = Blueprint('tables_template', __name__)


@tables_template_bp.route('/tabelas')
@login_required_template
def tables_page(current_user):
    """Render tables management page"""
    connections = DatabaseConnection.query.filter_by(
        user_id=current_user.id,
        is_active=True
    ).all()
    return render_template('tables.html', connections=connections, current_user=current_user)

