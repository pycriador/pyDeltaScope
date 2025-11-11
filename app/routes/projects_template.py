from flask import Blueprint, render_template
from app.models.project import Project
from app.models.database_connection import DatabaseConnection
from app.utils.security import login_required_template

projects_template_bp = Blueprint('projects_template', __name__)


@projects_template_bp.route('/projetos')
@login_required_template
def projects_page(current_user):
    """Render projects management page"""
    projects = Project.query.filter_by(
        user_id=current_user.id,
        is_active=True
    ).all()
    connections = DatabaseConnection.query.filter_by(
        user_id=current_user.id,
        is_active=True
    ).all()
    return render_template('projects.html', projects=projects, connections=connections, current_user=current_user)

