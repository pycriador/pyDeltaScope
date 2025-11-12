from flask import Blueprint, render_template, request, redirect, session
from app.models.database_connection import DatabaseConnection
from app.utils.security import login_required_template, permission_required_template, has_any_permission

connections_template_bp = Blueprint('connections_template', __name__)


@connections_template_bp.route('/conexoes')
@login_required_template
def connections_page(current_user):
    """Render connections management page - requires execute permission"""
    from app.utils.security import generate_token
    
    # Check if user can execute connections (view/list)
    if not has_any_permission(current_user, 'connections'):
        from flask import render_template as rt
        return rt('unauthorized.html', message='Você não tem permissão para visualizar conexões. Entre em contato com um administrador para solicitar esta permissão.', current_user=current_user), 403
    
    # Admins see all connections, regular users see only their own
    if current_user.is_admin:
        connections = DatabaseConnection.query.filter_by(is_active=True).all()
    else:
        connections = DatabaseConnection.query.filter_by(
            user_id=current_user.id,
            is_active=True
        ).all()
    
    # Generate token for API calls
    token = session.get('token') or generate_token(current_user)
    
    return render_template('connections.html', 
                         connections=connections, 
                         current_user=current_user,
                         auth_token=token)


@connections_template_bp.route('/conexoes/novo')
@permission_required_template('can_create_connections')
def new_connection_page(current_user):
    """Render new connection page - requires can_create_connections permission"""
    # Redirect to connections page which handles creation via modal
    # This route exists to catch unauthorized access attempts
    return redirect('/conexoes')


@connections_template_bp.route('/conexoes/<int:connection_id>/editar', methods=['GET'])
@login_required_template
def edit_connection_page(current_user, connection_id):
    """Render edit connection page"""
    print(f"[CONNECTIONS] Loading edit connection page for connection {connection_id}")
    try:
        # Get connection - admins can edit any, regular users only their own
        if current_user.is_admin:
            connection = DatabaseConnection.query.filter_by(
                id=connection_id,
                is_active=True
            ).first()
        else:
            connection = DatabaseConnection.query.filter_by(
                id=connection_id,
                user_id=current_user.id,
                is_active=True
            ).first()
        
        if not connection:
            return render_template('error.html', message='Conexão não encontrada', current_user=current_user), 404
        
        # Get decrypted config for editing
        decrypted_config = connection.get_decrypted_config()
        
        return render_template('edit_connection.html', 
                             connection=connection, 
                             decrypted_config=decrypted_config,
                             current_user=current_user)
    except Exception as e:
        import traceback
        print(f"[CONNECTIONS] Error loading edit connection page: {str(e)}")
        print(traceback.format_exc())
        return render_template('error.html', message=f'Erro ao carregar página de edição: {str(e)}'), 500

