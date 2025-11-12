from functools import wraps
from typing import Optional
from flask import request, jsonify, current_app, session, redirect, url_for, render_template
from werkzeug.security import generate_password_hash
import secrets
from datetime import datetime, timedelta
from app.models.user import User
from app import db


def generate_token(user: User) -> str:
    """Generate authentication token for user"""
    # Simple token generation - in production, use JWT or similar
    token = secrets.token_urlsafe(32)
    # Store token hash in user model (simplified - in production use separate token table)
    return token


def verify_token(token: str) -> Optional[User]:
    """Verify authentication token"""
    # Simplified token verification - in production, use proper JWT verification
    # For now, we'll use session-based auth with Werkzeug
    return None


def token_required(f):
    """Decorator for routes that require authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check for token in headers
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]  # Bearer TOKEN
            except IndexError:
                return jsonify({'message': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        # In a real implementation, verify token here
        # For now, we'll use session-based authentication
        user_id = request.headers.get('X-User-Id')
        if not user_id:
            return jsonify({'message': 'User ID is missing'}), 401
        
        try:
            user = User.query.get(int(user_id))
            if not user or not user.is_active:
                return jsonify({'message': 'Invalid user'}), 401
        except (ValueError, TypeError):
            return jsonify({'message': 'Invalid user ID'}), 401
        
        return f(user, *args, **kwargs)
    
    return decorated


def admin_required(f):
    """Decorator for routes that require admin privileges"""
    @wraps(f)
    @token_required
    def decorated(user, *args, **kwargs):
        if not user.is_admin:
            return jsonify({'message': 'Admin privileges required'}), 403
        return f(user, *args, **kwargs)
    
    return decorated


def login_required_template(f):
    """Decorator for template routes that require authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        user_id = session.get('user_id')
        print(f"[AUTH] login_required_template called for {f.__name__}")
        print(f"[AUTH] user_id from session: {user_id}")
        print(f"[AUTH] Session keys: {list(session.keys())}")
        print(f"[AUTH] Session data: {dict(session)}")
        
        if not user_id:
            print("[AUTH] No user_id in session, redirecting to /")
            return redirect('/')
        
        try:
            user = User.query.get(int(user_id))
            print(f"[AUTH] User found: {user.username if user else 'None'}, Active: {user.is_active if user else 'N/A'}, Admin: {user.is_admin if user else 'N/A'}")
            if not user or not user.is_active:
                print("[AUTH] User not found or inactive, clearing session")
                session.clear()
                return redirect('/')
            
            # Pre-load groups to avoid lazy loading issues in templates
            try:
                # Handle both dynamic query and list
                if hasattr(user.groups, 'all'):
                    _ = list(user.groups.all())
                else:
                    _ = list(user.groups)
                print(f"[AUTH] Pre-loaded groups for user {user.username}")
            except Exception as e:
                print(f"[AUTH] Warning: Could not pre-load groups: {e}")
        except (ValueError, TypeError) as e:
            print(f"[AUTH] Error getting user: {e}")
            import traceback
            print(traceback.format_exc())
            session.clear()
            return redirect('/')
        
        print(f"[AUTH] Authentication successful for {user.username}, calling {f.__name__}")
        return f(user, *args, **kwargs)
    
    return decorated


def admin_required_template(f):
    """Decorator for template routes that require admin privileges"""
    @wraps(f)
    @login_required_template
    def decorated(user, *args, **kwargs):
        print(f"[ADMIN CHECK] Checking admin access for user: {user.username if user else 'None'}, is_admin: {user.is_admin if user else 'N/A'}")
        if not user or not user.is_admin:
            print(f"[ADMIN CHECK] Access denied - user is not admin")
            return render_template('unauthorized.html', message='Acesso negado. Apenas administradores podem acessar esta página.', current_user=user), 403
        try:
            print(f"[ADMIN CHECK] Access granted, calling {f.__name__}")
            return f(user, *args, **kwargs)
        except Exception as e:
            import traceback
            print(f"[ADMIN CHECK] Error in {f.__name__}: {str(e)}")
            print(traceback.format_exc())
            return render_template('error.html', message=f'Erro ao carregar página: {str(e)}', current_user=user), 500
    
    return decorated


def has_permission(user: User, permission_name: str) -> bool:
    """Check if user has a specific permission (admin or via groups)"""
    if not user:
        return False
    
    # Admins have all permissions
    if user.is_admin:
        return True
    
    # Check group permissions
    try:
        # Handle both dynamic query and list
        if hasattr(user.groups, 'all'):
            groups = list(user.groups.all())
        else:
            groups = list(user.groups)
        
        for group in groups:
            if hasattr(group, permission_name) and getattr(group, permission_name):
                return True
    except Exception as e:
        print(f"[PERMISSION CHECK] Error checking permission {permission_name}: {e}")
    
    return False


def has_create_permission(user: User, functionality: str) -> bool:
    """Check if user can create for a specific functionality"""
    permission_name = f'can_create_{functionality}'
    return has_permission(user, permission_name)


def has_execute_permission(user: User, functionality: str) -> bool:
    """Check if user can execute for a specific functionality"""
    permission_name = f'can_execute_{functionality}'
    return has_permission(user, permission_name)


def has_any_permission(user: User, functionality: str) -> bool:
    """Check if user can either create OR execute for a specific functionality"""
    return has_create_permission(user, functionality) or has_execute_permission(user, functionality)


def get_users_with_execute_permission(functionality: str) -> list:
    """
    Get list of user IDs that have execute permission for a specific functionality.
    Returns list of user IDs (including admins).
    """
    from app.models.group import Group, user_groups
    
    # Get all admin users
    admin_users = User.query.filter_by(is_admin=True, is_active=True).all()
    admin_user_ids = [u.id for u in admin_users]
    
    # Get groups with execute permission for this functionality
    permission_name = f'can_execute_{functionality}'
    
    # Use getattr to dynamically access the column attribute
    permission_column = getattr(Group, permission_name, None)
    if permission_column is None:
        # Permission doesn't exist, return only admins
        return admin_user_ids
    
    groups_with_permission = Group.query.filter(permission_column == True).all()
    
    if not groups_with_permission:
        # Only admins have permission
        return admin_user_ids
    
    # Get all user IDs from these groups
    user_ids_set = set(admin_user_ids)
    
    for group in groups_with_permission:
        # Get users in this group
        group_users = group.users.filter_by(is_active=True).all()
        for user in group_users:
            user_ids_set.add(user.id)
    
    return list(user_ids_set)


def permission_required_template(permission_name):
    """Decorator factory for template routes that require specific group permissions"""
    def decorator(f):
        @wraps(f)
        @login_required_template
        def decorated(user, *args, **kwargs):
            print(f"[PERMISSION CHECK] Checking {permission_name} for user: {user.username if user else 'None'}")
            
            if not has_permission(user, permission_name):
                print(f"[PERMISSION CHECK] Access denied - user does not have {permission_name}")
                permission_messages = {
                    # Connections
                    'can_create_connections': 'Você não tem permissão para criar conexões. Entre em contato com um administrador para solicitar esta permissão.',
                    'can_execute_connections': 'Você não tem permissão para executar conexões. Entre em contato com um administrador para solicitar esta permissão.',
                    # Projects
                    'can_create_projects': 'Você não tem permissão para criar projetos. Entre em contato com um administrador para solicitar esta permissão.',
                    'can_execute_projects': 'Você não tem permissão para executar projetos. Entre em contato com um administrador para solicitar esta permissão.',
                    # Tables
                    'can_create_tables': 'Você não tem permissão para criar tabelas. Entre em contato com um administrador para solicitar esta permissão.',
                    'can_execute_tables': 'Você não tem permissão para executar tabelas. Entre em contato com um administrador para solicitar esta permissão.',
                    # Users
                    'can_create_users': 'Você não tem permissão para criar usuários. Entre em contato com um administrador para solicitar esta permissão.',
                    'can_execute_users': 'Você não tem permissão para executar usuários. Entre em contato com um administrador para solicitar esta permissão.',
                    # Groups
                    'can_create_groups': 'Você não tem permissão para criar grupos. Entre em contato com um administrador para solicitar esta permissão.',
                    'can_execute_groups': 'Você não tem permissão para executar grupos. Entre em contato com um administrador para solicitar esta permissão.',
                    # Comparison Reports
                    'can_create_comparison_reports': 'Você não tem permissão para criar relatórios de comparação. Entre em contato com um administrador para solicitar esta permissão.',
                    'can_execute_comparison_reports': 'Você não tem permissão para executar relatórios de comparação. Entre em contato com um administrador para solicitar esta permissão.',
                    # Consistency Reports
                    'can_create_consistency_reports': 'Você não tem permissão para criar relatórios de consistência. Entre em contato com um administrador para solicitar esta permissão.',
                    'can_execute_consistency_reports': 'Você não tem permissão para executar relatórios de consistência. Entre em contato com um administrador para solicitar esta permissão.',
                    # Dashboard
                    'can_create_dashboard': 'Você não tem permissão para criar dashboards. Entre em contato com um administrador para solicitar esta permissão.',
                    'can_execute_dashboard': 'Você não tem permissão para executar dashboards. Entre em contato com um administrador para solicitar esta permissão.',
                    # Comparison
                    'can_create_comparison': 'Você não tem permissão para criar comparações. Entre em contato com um administrador para solicitar esta permissão.',
                    'can_execute_comparison': 'Você não tem permissão para executar comparações. Entre em contato com um administrador para solicitar esta permissão.',
                    # Scheduled Tasks
                    'can_create_scheduled_tasks': 'Você não tem permissão para criar agendamentos. Entre em contato com um administrador para solicitar esta permissão.',
                    'can_execute_scheduled_tasks': 'Você não tem permissão para executar agendamentos. Entre em contato com um administrador para solicitar esta permissão.',
                    # Webhooks
                    'can_create_webhooks': 'Você não tem permissão para criar webhooks. Entre em contato com um administrador para solicitar esta permissão.',
                    'can_execute_webhooks': 'Você não tem permissão para executar webhooks. Entre em contato com um administrador para solicitar esta permissão.',
                    # Data Consistency
                    'can_create_data_consistency': 'Você não tem permissão para criar configurações de consistência de dados. Entre em contato com um administrador para solicitar esta permissão.',
                    'can_execute_data_consistency': 'Você não tem permissão para executar verificações de consistência de dados. Entre em contato com um administrador para solicitar esta permissão.',
                    # Legacy permissions
                    'can_view_dashboards': 'Você não tem permissão para visualizar dashboards. Entre em contato com um administrador para solicitar esta permissão.',
                    'can_edit_tables': 'Você não tem permissão para editar tabelas. Entre em contato com um administrador para solicitar esta permissão.',
                    'can_view_tables': 'Você não tem permissão para visualizar tabelas. Entre em contato com um administrador para solicitar esta permissão.',
                    'can_view_reports': 'Você não tem permissão para visualizar relatórios. Entre em contato com um administrador para solicitar esta permissão.',
                    'can_download_reports': 'Você não tem permissão para baixar relatórios. Entre em contato com um administrador para solicitar esta permissão.'
                }
                message = permission_messages.get(permission_name, 'Você não tem permissão para acessar este recurso.')
                # Try to get current_user from session for template context
                from flask import session
                from app.models.user import User
                user = None
                try:
                    user_id = session.get('user_id')
                    if user_id:
                        user = User.query.get(int(user_id))
                except:
                    pass
                return render_template('unauthorized.html', message=message, current_user=user), 403
            
            print(f"[PERMISSION CHECK] Access granted - user has {permission_name}")
            return f(user, *args, **kwargs)
        
        return decorated
    return decorator

