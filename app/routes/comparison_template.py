from flask import Blueprint, render_template, request, redirect, url_for
from app.models.project import Project
from app.utils.security import login_required_template

comparison_template_bp = Blueprint('comparison_template', __name__)


@comparison_template_bp.route('/comparacao')
@login_required_template
def comparison_page(current_user):
    """Render comparison page"""
    projects = Project.query.filter_by(
        user_id=current_user.id,
        is_active=True
    ).all()
    
    return render_template('comparison.html', 
                         projects=projects, 
                         current_user=current_user)


@comparison_template_bp.route('/comparacao/<int:project_id>/execution')
@login_required_template
def comparison_execution_page(current_user, project_id):
    """Render comparison execution page"""
    # Get project and verify ownership
    project = Project.query.filter_by(
        id=project_id,
        user_id=current_user.id,
        is_active=True
    ).first()
    
    if not project:
        return render_template('error.html', message='Projeto não encontrado'), 404
    
    return render_template('comparison_execution.html', 
                         project=project, 
                         current_user=current_user)

