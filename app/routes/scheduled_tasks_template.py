from flask import Blueprint, render_template
from app.models.project import Project
from app.utils.security import login_required_template

scheduled_tasks_template_bp = Blueprint('scheduled_tasks_template', __name__)


@scheduled_tasks_template_bp.route('/agendamentos')
@login_required_template
def scheduled_tasks_page(current_user):
    """Render scheduled tasks management page"""
    projects = Project.query.filter_by(
        user_id=current_user.id,
        is_active=True
    ).all()
    
    return render_template('scheduled_tasks.html', 
                         projects=projects, 
                         current_user=current_user)

