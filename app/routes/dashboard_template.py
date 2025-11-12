from flask import Blueprint, render_template, request
from app.models.project import Project
from app.utils.security import login_required_template

dashboard_template_bp = Blueprint('dashboard_template', __name__)


@dashboard_template_bp.route('/dashboard')
@login_required_template
def dashboard_page(current_user):
    """Render dashboard page"""
    # Admins see all projects, regular users see only their own
    if current_user.is_admin:
        projects = Project.query.filter_by(is_active=True).all()
    else:
        projects = Project.query.filter_by(
            user_id=current_user.id,
            is_active=True
        ).all()
    
    # Get selected project from query parameter
    selected_project_id = request.args.get('project_id', type=int)
    selected_project = None
    if selected_project_id:
        if current_user.is_admin:
            selected_project = Project.query.filter_by(id=selected_project_id).first()
        else:
            selected_project = Project.query.filter_by(
                id=selected_project_id,
                user_id=current_user.id
            ).first()
    
    # Get date filters from query parameters
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    
    return render_template('dashboard.html', 
                         projects=projects, 
                         selected_project=selected_project,
                         start_date=start_date,
                         end_date=end_date,
                         current_user=current_user)

