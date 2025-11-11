from flask import Blueprint, render_template, request, redirect, url_for
from app.models.user import User
from app.models.group import Group
from app import db
from app.utils.security import admin_required_template

users_template_bp = Blueprint('users_template', __name__)


@users_template_bp.route('/usuarios')
@admin_required_template
def users_page(current_user):
    """Render users management page"""
    print(f"[USERS] Loading users page for user: {current_user.username}")
    try:
        # Load users with their groups to avoid lazy loading issues
        users = User.query.all()
        print(f"[USERS] Found {len(users)} users")
        
        # Pre-load groups for each user to avoid lazy loading in template
        user_groups_dict = {}
        for user in users:
            try:
                # Handle both dynamic query and list
                if hasattr(user.groups, 'all'):
                    groups_list = user.groups.all()
                else:
                    groups_list = user.groups
                user_groups_dict[user.id] = list(groups_list)
                print(f"[USERS] User {user.username} has {len(groups_list)} groups")
            except Exception as e:
                print(f"[USERS] Error loading groups for user {user.id}: {e}")
                user_groups_dict[user.id] = []
        
        groups = Group.query.all()
        print(f"[USERS] Found {len(groups)} groups")
        
        print(f"[USERS] Rendering template with {len(users)} users")
        return render_template('users.html', users=users, groups=groups, user_groups_dict=user_groups_dict, current_user=current_user)
    except Exception as e:
        import traceback
        print(f"[USERS] Error loading users page: {str(e)}")
        print(traceback.format_exc())
        return render_template('error.html', message=f'Erro ao carregar usuários: {str(e)}'), 500


@users_template_bp.route('/usuarios/novo')
@admin_required_template
def create_user_page(current_user):
    """Render create user page"""
    print(f"[USERS] Loading create user page for admin: {current_user.username}")
    try:
        groups = Group.query.all()
        return render_template('create_user.html', groups=groups, current_user=current_user)
    except Exception as e:
        import traceback
        print(f"[USERS] Error loading create user page: {str(e)}")
        print(traceback.format_exc())
        return render_template('error.html', message=f'Erro ao carregar página de criação de usuário: {str(e)}'), 500


@users_template_bp.route('/usuarios/<int:user_id>/senha', methods=['GET', 'POST'])
@admin_required_template
def change_password_page(current_user, user_id):
    """Render change password page and handle password change"""
    print(f"[USERS] Loading change password page for user {user_id}")
    try:
        user = User.query.get(user_id)
        if not user:
            return render_template('error.html', message='Usuário não encontrado'), 404
        
        if request.method == 'POST':
            password = request.form.get('password', '').strip()
            confirm_password = request.form.get('confirm_password', '').strip()
            
            # Validation
            if not password or not confirm_password:
                return render_template('change_password.html', 
                                     user=user, 
                                     current_user=current_user,
                                     error='Preencha todos os campos')
            
            if len(password) < 6:
                return render_template('change_password.html', 
                                     user=user, 
                                     current_user=current_user,
                                     error='A senha deve ter pelo menos 6 caracteres')
            
            if password != confirm_password:
                return render_template('change_password.html', 
                                     user=user, 
                                     current_user=current_user,
                                     error='As senhas não coincidem')
            
            # Change password
            try:
                user.set_password(password)
                db.session.commit()
                
                return render_template('change_password.html', 
                                     user=user, 
                                     current_user=current_user,
                                     success='Senha alterada com sucesso!')
            except Exception as e:
                db.session.rollback()
                return render_template('change_password.html', 
                                     user=user, 
                                     current_user=current_user,
                                     error=f'Erro ao alterar senha: {str(e)}')
        
        # GET request - show form
        return render_template('change_password.html', user=user, current_user=current_user)
    except Exception as e:
        import traceback
        print(f"[USERS] Error loading change password page: {str(e)}")
        print(traceback.format_exc())
        return render_template('error.html', message=f'Erro ao carregar página de alteração de senha: {str(e)}'), 500

