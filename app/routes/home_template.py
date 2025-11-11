from flask import Blueprint, render_template, redirect, session
from app.models.user import User
from app.utils.security import login_required_template

home_template_bp = Blueprint('home_template', __name__)


@home_template_bp.route('/home')
@login_required_template
def home_page(current_user):
    """Render home page for authenticated users"""
    # Check user permissions
    has_any_permission = False
    if current_user.is_admin:
        has_any_permission = True
    else:
        # Check if user has any permissions through groups
        for group in current_user.groups:
            if (group.can_create_connections or group.can_create_projects or 
                group.can_view_dashboards or group.can_edit_tables or 
                group.can_view_tables or group.can_view_reports or 
                group.can_download_reports):
                has_any_permission = True
                break
    
    return render_template('home.html', current_user=current_user, has_any_permission=has_any_permission)

