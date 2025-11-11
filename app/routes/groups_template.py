from flask import Blueprint, render_template
from app.models.group import Group
from app.utils.security import admin_required_template
from app import db

groups_template_bp = Blueprint('groups_template', __name__)


@groups_template_bp.route('/grupos')
@admin_required_template
def groups_page(current_user):
    """Render groups management page"""
    print(f"[GROUPS] Loading groups page for user: {current_user.username}")
    try:
        groups = Group.query.all()
        print(f"[GROUPS] Found {len(groups)} groups")
        
        # Create a dictionary mapping group IDs to user counts
        group_user_counts = {}
        for group in groups:
            try:
                user_count = group.users.count()
                group_user_counts[group.id] = user_count
                print(f"[GROUPS] Group {group.name} has {user_count} users")
            except Exception as e:
                print(f"[GROUPS] Error counting users for group {group.id}: {e}")
                group_user_counts[group.id] = 0
        
        print(f"[GROUPS] Rendering template with {len(groups)} groups")
        return render_template('groups.html', groups=groups, group_user_counts=group_user_counts, current_user=current_user)
    except Exception as e:
        import traceback
        print(f"[GROUPS] Error loading groups page: {str(e)}")
        print(traceback.format_exc())
        return render_template('error.html', message=f'Erro ao carregar grupos: {str(e)}'), 500

