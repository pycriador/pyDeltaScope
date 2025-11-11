from flask import Blueprint, render_template
from app.models.project import Project
from app.utils.security import login_required_template

reports_template_bp = Blueprint('reports_template', __name__)


@reports_template_bp.route('/relatorios')
@login_required_template
def reports_page(current_user):
    """Render reports page"""
    projects = Project.query.filter_by(
        user_id=current_user.id,
        is_active=True
    ).all()
    return render_template('reports.html', projects=projects, current_user=current_user)

