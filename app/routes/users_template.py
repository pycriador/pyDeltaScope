from flask import Blueprint, render_template
from app.models.user import User
from app.models.group import Group
from app.utils.security import admin_required_template

users_template_bp = Blueprint('users_template', __name__)


@users_template_bp.route('/usuarios')
@admin_required_template
def users_page(current_user):
    """Render users management page"""
    print(f"[USERS] Loading users page for user: {current_user.username}")
    try:
        users = User.query.all()
        print(f"[USERS] Found {len(users)} users")
        
        groups = Group.query.all()
        print(f"[USERS] Found {len(groups)} groups")
        
        print(f"[USERS] Rendering template with {len(users)} users")
        return render_template('users.html', users=users, groups=groups, current_user=current_user)
    except Exception as e:
        import traceback
        print(f"[USERS] Error loading users page: {str(e)}")
        print(traceback.format_exc())
        return render_template('error.html', message=f'Erro ao carregar usuários: {str(e)}'), 500

