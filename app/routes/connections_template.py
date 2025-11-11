from flask import Blueprint, render_template
from app.models.database_connection import DatabaseConnection
from app.utils.security import login_required_template

connections_template_bp = Blueprint('connections_template', __name__)


@connections_template_bp.route('/conexoes')
@login_required_template
def connections_page(current_user):
    """Render connections management page"""
    connections = DatabaseConnection.query.filter_by(
        user_id=current_user.id,
        is_active=True
    ).all()
    return render_template('connections.html', connections=connections, current_user=current_user)

