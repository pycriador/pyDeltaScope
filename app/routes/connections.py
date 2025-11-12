from flask import Blueprint, request, jsonify
from app.models.database_connection import DatabaseConnection
from app.models.user import User
from app import db
from app.utils.security import token_required
from app.utils.encryption import encrypt_db_config
from app.services.database import DatabaseService

connections_bp = Blueprint('connections', __name__)


@connections_bp.route('', methods=['GET'])
@token_required
def get_connections(user):
    """Get all database connections - admins see all, regular users see only their own"""
    if user.is_admin:
        connections = DatabaseConnection.query.filter_by(is_active=True).all()
    else:
        connections = DatabaseConnection.query.filter_by(
            user_id=user.id, 
            is_active=True
        ).all()
    return jsonify({
        'connections': [conn.to_dict() for conn in connections]
    }), 200


@connections_bp.route('/<int:connection_id>', methods=['GET'])
@token_required
def get_connection(user, connection_id):
    """Get a specific database connection - admins can see any, regular users only their own"""
    if user.is_admin:
        connection = DatabaseConnection.query.filter_by(id=connection_id).first()
    else:
        connection = DatabaseConnection.query.filter_by(
            id=connection_id, 
            user_id=user.id
        ).first()
    
    if not connection:
        return jsonify({'message': 'Connection not found'}), 404
    
    return jsonify({'connection': connection.to_dict()}), 200


@connections_bp.route('', methods=['POST'])
@token_required
def create_connection(user):
    """Create a new database connection"""
    data = request.get_json()
    
    if not data or not data.get('name') or not data.get('db_type') or not data.get('db_config'):
        return jsonify({'message': 'Missing required fields'}), 400
    
    # Encrypt password in config
    encrypted_config = encrypt_db_config(data['db_config'])
    
    try:
        connection = DatabaseConnection(
            name=data['name'],
            description=data.get('description', ''),
            db_type=data['db_type'],
            db_config=encrypted_config,
            user_id=user.id
        )
        
        db.session.add(connection)
        db.session.commit()
        
        return jsonify({
            'message': 'Connection created successfully',
            'connection': connection.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error creating connection: {str(e)}'}), 500


@connections_bp.route('/<int:connection_id>', methods=['PUT'])
@token_required
def update_connection(user, connection_id):
    """Update a database connection - admins can update any, regular users only their own"""
    if user.is_admin:
        connection = DatabaseConnection.query.filter_by(id=connection_id).first()
    else:
        connection = DatabaseConnection.query.filter_by(
            id=connection_id, 
            user_id=user.id
        ).first()
    
    if not connection:
        return jsonify({'message': 'Connection not found'}), 404
    
    data = request.get_json()
    
    if 'name' in data:
        connection.name = data['name']
    if 'description' in data:
        connection.description = data['description']
    if 'db_type' in data:
        connection.db_type = data['db_type']
    if 'db_config' in data:
        new_config = data['db_config']
        
        # If password is empty/not provided for MariaDB/MySQL, keep the existing encrypted password
        if connection.db_type.lower() in ['mariadb', 'mysql']:
            if not new_config.get('password') or new_config.get('password') == '':
                # Get current decrypted config to preserve password
                current_decrypted = connection.get_decrypted_config()
                if current_decrypted and current_decrypted.get('password'):
                    # Keep the existing password
                    new_config['password'] = current_decrypted['password']
                else:
                    return jsonify({
                        'message': 'Senha é obrigatória para conexões MariaDB/MySQL. Se deseja manter a senha atual, ela deve estar configurada corretamente.'
                    }), 400
        
        connection.db_config = encrypt_db_config(new_config)
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Connection updated successfully',
            'connection': connection.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error updating connection: {str(e)}'}), 500


@connections_bp.route('/<int:connection_id>', methods=['DELETE'])
@token_required
def delete_connection(user, connection_id):
    """Delete a database connection (soft delete) - admins can delete any, regular users only their own"""
    if user.is_admin:
        connection = DatabaseConnection.query.filter_by(id=connection_id).first()
    else:
        connection = DatabaseConnection.query.filter_by(
            id=connection_id, 
            user_id=user.id
        ).first()
    
    if not connection:
        return jsonify({'message': 'Connection not found'}), 404
    
    connection.is_active = False
    
    try:
        db.session.commit()
        return jsonify({'message': 'Connection deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error deleting connection: {str(e)}'}), 500


@connections_bp.route('/<int:connection_id>/test', methods=['POST'])
@token_required
def test_connection(user, connection_id):
    """Test a database connection - admins can test any, regular users only their own"""
    if user.is_admin:
        connection = DatabaseConnection.query.filter_by(id=connection_id).first()
    else:
        connection = DatabaseConnection.query.filter_by(
            id=connection_id, 
            user_id=user.id
        ).first()
    
    if not connection:
        return jsonify({'message': 'Connection not found'}), 404
    
    try:
        # Get decrypted config
        decrypted_config = connection.get_decrypted_config()
        decrypted_config['type'] = connection.db_type
        
        # Verify password exists
        if connection.db_type.lower() in ['mariadb', 'mysql']:
            password = decrypted_config.get('password', '')
            if not password:
                return jsonify({
                    'success': False,
                    'message': 'Senha não encontrada ou não foi possível descriptografar. Verifique se a ENCRYPTION_KEY está correta ou recrie a conexão.'
                }), 200
        
        # Test connection (already decrypted, so pass already_decrypted=True)
        engine = DatabaseService.get_engine(decrypted_config, already_decrypted=True)
        with engine.connect() as conn:
            from sqlalchemy import text
            conn.execute(text("SELECT 1"))
        
        return jsonify({
            'success': True,
            'message': 'Connection successful'
        }), 200
    except Exception as e:
        error_msg = str(e)
        # Check if it's an authentication error
        if 'Access denied' in error_msg or '1045' in error_msg:
            return jsonify({
                'success': False,
                'message': 'Erro de autenticação: Senha incorreta ou não foi possível descriptografar. Verifique a ENCRYPTION_KEY ou recrie a conexão com a senha correta.'
            }), 200
        return jsonify({
            'success': False,
            'message': f'Connection failed: {error_msg}'
        }), 200


@connections_bp.route('/<int:connection_id>/tables', methods=['GET'])
@token_required
def get_connection_tables(user, connection_id):
    """Get tables from a database connection - admins can access any, regular users only their own"""
    if user.is_admin:
        connection = DatabaseConnection.query.filter_by(id=connection_id).first()
    else:
        connection = DatabaseConnection.query.filter_by(
            id=connection_id, 
            user_id=user.id
        ).first()
    
    if not connection:
        return jsonify({'message': 'Connection not found'}), 404
    
    try:
        # Get decrypted config
        decrypted_config = connection.get_decrypted_config()
        if not decrypted_config:
            return jsonify({
                'message': 'Configuração de conexão não encontrada'
            }), 400
            
        decrypted_config['type'] = connection.db_type
        
        # Verify password exists
        if connection.db_type.lower() in ['mariadb', 'mysql']:
            password = decrypted_config.get('password', '')
            if not password:
                return jsonify({
                    'message': 'Senha não encontrada ou não foi possível descriptografar. Verifique se a ENCRYPTION_KEY está correta ou recrie a conexão.'
                }), 400
        
        # Get tables (already decrypted, so pass already_decrypted=True)
        try:
            engine = DatabaseService.get_engine(decrypted_config, already_decrypted=True)
        except Exception as engine_error:
            return jsonify({
                'message': f'Erro ao criar conexão com o banco: {str(engine_error)}'
            }), 500
        
        try:
            tables = DatabaseService.get_tables(engine)
        except Exception as tables_error:
            return jsonify({
                'message': f'Erro ao listar tabelas: {str(tables_error)}'
            }), 500
        
        return jsonify({
            'tables': tables
        }), 200
    except Exception as e:
        import traceback
        error_msg = str(e)
        traceback.print_exc()  # Print full traceback for debugging
        
        # Check if it's an authentication error
        if 'Access denied' in error_msg or '1045' in error_msg:
            return jsonify({
                'message': 'Erro de autenticação: Senha incorreta ou não foi possível descriptografar. Verifique a ENCRYPTION_KEY ou recrie a conexão com a senha correta.'
            }), 400
        
        # Return error with details
        return jsonify({
            'message': f'Erro ao listar tabelas: {error_msg}',
            'error_type': type(e).__name__
        }), 500


@connections_bp.route('/<int:connection_id>/tables/<table_name>/info', methods=['GET'])
@token_required
def get_table_info(user, connection_id, table_name):
    """Get table information - admins can access any, regular users only their own"""
    if user.is_admin:
        connection = DatabaseConnection.query.filter_by(id=connection_id).first()
    else:
        connection = DatabaseConnection.query.filter_by(
            id=connection_id, 
            user_id=user.id
        ).first()
    
    if not connection:
        return jsonify({'message': 'Connection not found'}), 404
    
    try:
        # Get decrypted config
        decrypted_config = connection.get_decrypted_config()
        decrypted_config['type'] = connection.db_type
        
        # Get table info (already decrypted, so pass already_decrypted=True)
        engine = DatabaseService.get_engine(decrypted_config, already_decrypted=True)
        columns = DatabaseService.get_table_columns(engine, table_name)
        primary_keys = DatabaseService.get_primary_keys(engine, table_name)
        row_count = DatabaseService.get_table_row_count(engine, table_name)
        
        return jsonify({
            'columns': columns,
            'primary_keys': primary_keys,
            'row_count': row_count
        }), 200
    except Exception as e:
        return jsonify({'message': f'Error getting table info: {str(e)}'}), 500

