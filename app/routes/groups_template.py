from flask import Blueprint, render_template, request, redirect, session
from app.models.group import Group
from app.models.user import User
from app.utils.security import admin_required_template, generate_token
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


@groups_template_bp.route('/grupos/<int:group_id>/editar', methods=['GET', 'POST'])
@admin_required_template
def edit_group_page(current_user, group_id):
    """Render edit group page and handle group update"""
    try:
        group = Group.query.get(group_id)
        
        if not group:
            return render_template('error.html', message='Grupo não encontrado'), 404
        
        # Generate token for API calls
        token = session.get('token') or generate_token(current_user)
        
        if request.method == 'POST':
            # Handle form submission via API (will be handled by JavaScript)
            return redirect('/grupos')
        
        # GET request - show edit form
        return render_template('edit_group.html', 
                             group=group, 
                             current_user=current_user,
                             auth_token=token)
    except Exception as e:
        import traceback
        print(f"[GROUPS] Error loading edit group page: {str(e)}")
        print(traceback.format_exc())
        return render_template('error.html', message=f'Erro ao carregar página de edição: {str(e)}'), 500


@groups_template_bp.route('/grupos/<int:group_id>/usuarios')
@admin_required_template
def group_users_page(current_user, group_id):
    """Render group users management page"""
    try:
        group = Group.query.get(group_id)
        
        if not group:
            return render_template('error.html', message='Grupo não encontrado'), 404
        
        # Get all users in the group
        group_users = group.users.all()
        
        # Get all users (for adding to group)
        all_users = User.query.filter_by(is_active=True).all()
        
        # Generate token for API calls
        token = session.get('token') or generate_token(current_user)
        
        return render_template('group_users.html', 
                             group=group,
                             group_users=group_users,
                             all_users=all_users,
                             current_user=current_user,
                             auth_token=token)
    except Exception as e:
        import traceback
        print(f"[GROUPS] Error loading group users page: {str(e)}")
        print(traceback.format_exc())
        return render_template('error.html', message=f'Erro ao carregar página de usuários: {str(e)}'), 500

