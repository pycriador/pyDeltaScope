from flask import Blueprint, render_template, redirect, session
from app.models.user import User
from app.utils.security import login_required_template, has_any_permission as check_any_permission

home_template_bp = Blueprint('home_template', __name__)


@home_template_bp.route('/home')
@login_required_template
def home_page(current_user):
    """Render home page for authenticated users"""
    # Check if user has any permissions (create or execute for any functionality)
    user_has_permission = False
    if current_user.is_admin:
        user_has_permission = True
    else:
        # Check all functionalities
        functionalities = [
            'connections', 'projects', 'tables', 'users', 'groups',
            'comparison_reports', 'consistency_reports', 'dashboard',
            'comparison', 'scheduled_tasks', 'webhooks', 'data_consistency'
        ]
        for func in functionalities:
            if check_any_permission(current_user, func):
                user_has_permission = True
                break
    
    return render_template('home.html', current_user=current_user, has_any_permission=user_has_permission)

