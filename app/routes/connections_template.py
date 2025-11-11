from flask import Blueprint, render_template, request, redirect
from app.models.database_connection import DatabaseConnection
from app.utils.security import login_required_template

connections_template_bp = Blueprint('connections_template', __name__)


@connections_template_bp.route('/conexoes')
@login_required_template
def connections_page(current_user):
    """Render connections management page"""
    connections = DatabaseConnection.query.filter_by(
        user_id=current_user.id,
        is_active=True
    ).all()
    return render_template('connections.html', connections=connections, current_user=current_user)


@connections_template_bp.route('/conexoes/<int:connection_id>/editar', methods=['GET'])
@login_required_template
def edit_connection_page(current_user, connection_id):
    """Render edit connection page"""
    print(f"[CONNECTIONS] Loading edit connection page for connection {connection_id}")
    try:
        # Get connection and verify ownership
        connection = DatabaseConnection.query.filter_by(
            id=connection_id,
            user_id=current_user.id,
            is_active=True
        ).first()
        
        if not connection:
            return render_template('error.html', message='Conexão não encontrada'), 404
        
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

