from flask import Blueprint, render_template, request
from app.models.database_connection import DatabaseConnection
from app.utils.security import login_required_template
from app.services.database import DatabaseService

tables_template_bp = Blueprint('tables_template', __name__)


@tables_template_bp.route('/tabelas')
@login_required_template
def tables_page(current_user):
    """Render tables management page"""
    # Admins see all connections, regular users see only their own
    if current_user.is_admin:
        connections = DatabaseConnection.query.filter_by(is_active=True).all()
    else:
        connections = DatabaseConnection.query.filter_by(
            user_id=current_user.id,
            is_active=True
        ).all()
    return render_template('tables.html', 
                         connections=connections, 
                         current_user=current_user,
                         selected_connection_id=request.args.get('connection_id', type=int))


@tables_template_bp.route('/tabelas/<int:connection_id>/edit/<path:table_name>')
@login_required_template
def edit_table_page(current_user, connection_id, table_name):
    """Render table columns edit page"""
    # Get connection - admins can access any, regular users only their own
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
    
    # Get table columns
    try:
        decrypted_config = connection.get_decrypted_config()
        decrypted_config['type'] = connection.db_type
        
        engine = DatabaseService.get_engine(decrypted_config, already_decrypted=True)
        columns = DatabaseService.get_table_columns(engine, table_name)
        primary_keys = DatabaseService.get_primary_keys(engine, table_name)
        
        # Mark primary keys
        for col in columns:
            col['primary_key'] = col['name'] in primary_keys
        
    except Exception as e:
        import traceback
        print(f"[TABLES] Error loading table columns: {str(e)}")
        print(traceback.format_exc())
        return render_template('error.html', message=f'Erro ao carregar colunas da tabela: {str(e)}'), 500
    
    return render_template('edit_table.html', 
                         connection=connection, 
                         table_name=table_name,
                         columns=columns,
                         current_user=current_user)

