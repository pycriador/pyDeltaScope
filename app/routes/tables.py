from flask import Blueprint, request, jsonify
from datetime import datetime
from sqlalchemy import text, MetaData, Table, Column, inspect
from sqlalchemy.types import Integer, String, Text, DateTime, Date, Time, Float, Numeric, Boolean, LargeBinary, JSON
from app.utils.security import token_required
from app.services.database import DatabaseService
from app.models.database_connection import DatabaseConnection
from app.models.project import Project
from app.models.table_model_mapping import TableModelMapping
from app.services.table_mapper import TableMapper
from pathlib import Path
from app import db

tables_bp = Blueprint('tables', __name__)


@tables_bp.route('/test-connection', methods=['POST'])
@token_required
def test_connection(user):
    """Test database connection"""
    data = request.get_json()
    
    if not data or not data.get('db_config'):
        return jsonify({'message': 'Database configuration required'}), 400
    
    try:
        engine = DatabaseService.get_engine(data['db_config'])
        # Try to connect
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        return jsonify({
            'success': True,
            'message': 'Connection successful'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Connection failed: {str(e)}'
        }), 200


@tables_bp.route('/list', methods=['POST'])
@token_required
def list_tables(user):
    """List tables from a database"""
    data = request.get_json()
    
    if not data or not data.get('db_config'):
        return jsonify({'message': 'Database configuration required'}), 400
    
    try:
        engine = DatabaseService.get_engine(data['db_config'])
        tables = DatabaseService.get_tables(engine)
        
        return jsonify({
            'tables': tables
        }), 200
    except Exception as e:
        return jsonify({'message': f'Error listing tables: {str(e)}'}), 500


@tables_bp.route('/columns', methods=['POST'])
@token_required
def get_table_columns(user):
    """Get columns for a table"""
    data = request.get_json()
    
    if not data or not data.get('db_config') or not data.get('table_name'):
        return jsonify({'message': 'Database configuration and table name required'}), 400
    
    try:
        engine = DatabaseService.get_engine(data['db_config'])
        columns = DatabaseService.get_table_columns(engine, data['table_name'])
        primary_keys = DatabaseService.get_primary_keys(engine, data['table_name'])
        row_count = DatabaseService.get_table_row_count(engine, data['table_name'])
        
        return jsonify({
            'columns': columns,
            'primary_keys': primary_keys,
            'row_count': row_count
        }), 200
    except Exception as e:
        return jsonify({'message': f'Error getting table columns: {str(e)}'}), 500


@tables_bp.route('/preview', methods=['POST'])
@token_required
def preview_table(user):
    """Preview table data"""
    data = request.get_json()
    
    if not data or not data.get('db_config') or not data.get('table_name'):
        return jsonify({'message': 'Database configuration and table name required'}), 400
    
    try:
        engine = DatabaseService.get_engine(data['db_config'])
        limit = data.get('limit', 100)
        df = DatabaseService.get_table_data(engine, data['table_name'], limit=limit)
        
        # Convert DataFrame to JSON
        return jsonify({
            'data': df.to_dict(orient='records'),
            'columns': list(df.columns),
            'row_count': len(df)
        }), 200
    except Exception as e:
        return jsonify({'message': f'Error previewing table: {str(e)}'}), 500


@tables_bp.route('/update-primary-keys', methods=['POST'])
@token_required
def update_primary_keys(user):
    """Update primary keys for a table and regenerate models in projects"""
    data = request.get_json()
    
    if not data or not data.get('connection_id') or not data.get('table_name'):
        return jsonify({'message': 'Connection ID and table name required'}), 400
    
    connection_id = data['connection_id']
    table_name = data['table_name']
    primary_keys = data.get('primary_keys', [])
    
    # Verify connection belongs to user
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
        
        # Get table columns
        engine = DatabaseService.get_engine(decrypted_config, already_decrypted=True)
        columns = DatabaseService.get_table_columns(engine, table_name)
        
        # Update primary_key flag in columns
        for col in columns:
            col['primary_key'] = col['name'] in primary_keys
        
        # Find all projects that use this table
        projects = Project.query.filter(
            ((Project.source_connection_id == connection_id) & (Project.source_table == table_name)) |
            ((Project.target_connection_id == connection_id) & (Project.target_table == table_name))
        ).filter_by(user_id=user.id, is_active=True).all()
        
        updated_projects = []
        base_path = Path(__file__).parent.parent.parent
        
        for project in projects:
            # Determine if this is source or target table
            is_source = project.source_connection_id == connection_id and project.source_table == table_name
            
            # Regenerate model
            model_code = TableMapper.generate_model_code(table_name, columns, decrypted_config)
            model_path = TableMapper.save_model_file(
                project.name,
                table_name,
                model_code,
                base_path
            )
            
            # Update project model file path
            if is_source:
                # Could store source model path separately if needed
                project.model_file_path = str(model_path)
            
            updated_projects.append({
                'id': project.id,
                'name': project.name
            })
        
        db.session.commit()
        
        return jsonify({
            'message': f'Primary keys updated successfully. Models regenerated for {len(updated_projects)} project(s).',
            'updated_projects': updated_projects
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error updating primary keys: {str(e)}'}), 500


@tables_bp.route('/update-column-type', methods=['POST'])
@token_required
def update_column_type(user):
    """Update column type in database and regenerate models"""
    data = request.get_json()
    
    if not data or not data.get('connection_id') or not data.get('table_name') or not data.get('column_name') or not data.get('new_type'):
        return jsonify({'message': 'Connection ID, table name, column name and new type required'}), 400
    
    connection_id = data['connection_id']
    table_name = data['table_name']
    column_name = data['column_name']
    new_type = data['new_type']
    nullable = data.get('nullable', True)
    primary_key = data.get('primary_key', False)
    
    # Verify connection belongs to user
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
        engine = DatabaseService.get_engine(decrypted_config, already_decrypted=True)
        
        # Get current primary keys
        current_primary_keys = DatabaseService.get_primary_keys(engine, table_name)
        was_primary_key = column_name in current_primary_keys
        
        # If primary key status changed, update it in database
        if primary_key != was_primary_key:
            if connection.db_type.lower() in ['mariadb', 'mysql']:
                with engine.connect() as conn:
                    if primary_key:
                        # Add primary key constraint
                        # First, remove existing primary key if exists
                        if current_primary_keys:
                            alter_sql = f"ALTER TABLE `{table_name}` DROP PRIMARY KEY"
                            try:
                                conn.execute(text(alter_sql))
                            except Exception as e:
                                print(f"Warning: Could not drop primary key: {e}")
                        
                        # Add new primary key
                        alter_sql = f"ALTER TABLE `{table_name}` ADD PRIMARY KEY (`{column_name}`)"
                        conn.execute(text(alter_sql))
                    else:
                        # Remove primary key constraint
                        if was_primary_key:
                            alter_sql = f"ALTER TABLE `{table_name}` DROP PRIMARY KEY"
                            try:
                                conn.execute(text(alter_sql))
                            except Exception as e:
                                print(f"Warning: Could not drop primary key: {e}")
                    conn.commit()
            # Note: SQLite doesn't support ALTER TABLE for primary keys easily
        
        # Map SQLAlchemy type to database-specific type
        # For MariaDB/MySQL, use TINYINT(1) for Boolean instead of BOOLEAN
        # to avoid issues with existing data
        if connection.db_type.lower() in ['mariadb', 'mysql']:
            type_mapping = {
                'Integer': 'INTEGER',
                'BigInteger': 'BIGINT',
                'SmallInteger': 'SMALLINT',
                'String': 'VARCHAR(255)',
                'Text': 'TEXT',
                'DateTime': 'DATETIME',
                'Date': 'DATE',
                'Time': 'TIME',
                'Float': 'FLOAT',
                'Numeric': 'DECIMAL(10,2)',
                'Boolean': 'TINYINT(1)',  # Use TINYINT(1) for MySQL/MariaDB
                'LargeBinary': 'BLOB',
                'JSON': 'JSON'
            }
        else:
            type_mapping = {
                'Integer': 'INTEGER',
                'BigInteger': 'BIGINT',
                'SmallInteger': 'SMALLINT',
                'String': 'VARCHAR(255)',
                'Text': 'TEXT',
                'DateTime': 'DATETIME',
                'Date': 'DATE',
                'Time': 'TIME',
                'Float': 'FLOAT',
                'Numeric': 'DECIMAL(10,2)',
                'Boolean': 'BOOLEAN',
                'LargeBinary': 'BLOB',
                'JSON': 'JSON'
            }
        
        db_type = type_mapping.get(new_type, 'VARCHAR(255)')
        
        # Alter column type in database (SQLite/MariaDB specific)
        if connection.db_type.lower() == 'sqlite':
            # SQLite doesn't support ALTER COLUMN directly, need to recreate table
            # For now, just update the model file
            pass
        elif connection.db_type.lower() in ['mariadb', 'mysql']:
            with engine.connect() as conn:
                # For Boolean type, we need to handle existing data carefully
                # First, check if we're converting to Boolean
                if new_type == 'Boolean':
                    # Get current column type to see if we need to convert data
                    inspector = inspect(engine)
                    current_cols = inspector.get_columns(table_name)
                    current_col = next((c for c in current_cols if c['name'] == column_name), None)
                    
                    if current_col:
                        current_type = str(current_col['type']).upper()
                        # If converting from string/text, we need to handle data conversion
                        if 'VARCHAR' in current_type or 'TEXT' in current_type or 'CHAR' in current_type:
                            # First convert to INT, then to TINYINT(1)
                            # Convert 'true'/'false' strings to 1/0
                            alter_sql = f"""
                                ALTER TABLE `{table_name}` 
                                MODIFY COLUMN `{column_name}` TINYINT(1) 
                                {'NOT NULL' if not nullable else ''}
                            """
                            conn.execute(text(alter_sql))
                            # Update existing data: convert 'true'/'false' strings to 1/0
                            update_sql = f"""
                                UPDATE `{table_name}` 
                                SET `{column_name}` = CASE 
                                    WHEN LOWER(TRIM(`{column_name}`)) = 'true' THEN 1
                                    WHEN LOWER(TRIM(`{column_name}`)) = 'false' THEN 0
                                    WHEN `{column_name}` = '1' THEN 1
                                    WHEN `{column_name}` = '0' THEN 0
                                    ELSE 0
                                END
                            """
                            try:
                                conn.execute(text(update_sql))
                            except Exception as e:
                                print(f"Warning: Could not convert existing data: {e}")
                        else:
                            # Direct conversion to TINYINT(1)
                            alter_sql = f"ALTER TABLE `{table_name}` MODIFY COLUMN `{column_name}` TINYINT(1)"
                            if not nullable:
                                alter_sql += " NOT NULL"
                            conn.execute(text(alter_sql))
                    else:
                        # Column not found, just create it
                        alter_sql = f"ALTER TABLE `{table_name}` MODIFY COLUMN `{column_name}` TINYINT(1)"
                        if not nullable:
                            alter_sql += " NOT NULL"
                        conn.execute(text(alter_sql))
                else:
                    # For non-Boolean types, use standard ALTER
                    alter_sql = f"ALTER TABLE `{table_name}` MODIFY COLUMN `{column_name}` {db_type}"
                    if not nullable:
                        alter_sql += " NOT NULL"
                    conn.execute(text(alter_sql))
                
                conn.commit()
        
        # Get updated columns (refresh after potential primary key changes)
        columns = DatabaseService.get_table_columns(engine, table_name)
        
        # Update the specific column information
        for col in columns:
            if col['name'] == column_name:
                col['type'] = new_type
                col['nullable'] = nullable
                # Update primary key status from database (may have changed)
                updated_primary_keys = DatabaseService.get_primary_keys(engine, table_name)
                col['primary_key'] = col['name'] in updated_primary_keys
        
        # Find all projects that use this table
        projects = Project.query.filter(
            ((Project.source_connection_id == connection_id) & (Project.source_table == table_name)) |
            ((Project.target_connection_id == connection_id) & (Project.target_table == table_name))
        ).filter_by(user_id=user.id, is_active=True).all()
        
        # Update or create table model mapping
        mapping = TableModelMapping.query.filter_by(
            connection_id=connection_id,
            table_name=table_name,
            user_id=user.id
        ).first()
        
        base_path = Path(__file__).parent.parent.parent
        updated_projects = []
        
        # Use the first project's name for the model file (or a generic name if no projects)
        if projects:
            # Use the first project name for consistency
            project_name_for_model = projects[0].name
        else:
            # If no projects use this table, use connection name + table name
            project_name_for_model = f"{connection.name}_{table_name}"
        
        # Generate model code once (same for all projects using this table)
        model_code = TableMapper.generate_model_code(table_name, columns, decrypted_config)
        model_path = TableMapper.save_model_file(
            project_name_for_model,
            table_name,
            model_code,
            base_path
        )
        
        # Update or create mapping (only once, outside the loop)
        if not mapping:
            mapping = TableModelMapping(
                connection_id=connection_id,
                table_name=table_name,
                model_file_path=str(model_path),
                user_id=user.id
            )
            db.session.add(mapping)
        else:
            mapping.model_file_path = str(model_path)
            mapping.updated_at = datetime.utcnow()
        
        # Update all projects that use this table
        for project in projects:
            # Regenerate model for each project (in case project name changed)
            model_code = TableMapper.generate_model_code(table_name, columns, decrypted_config)
            model_path = TableMapper.save_model_file(
                project.name,
                table_name,
                model_code,
                base_path
            )
            
            # Update project model file path if source table
            if project.source_connection_id == connection_id and project.source_table == table_name:
                project.model_file_path = str(model_path)
            
            updated_projects.append({
                'id': project.id,
                'name': project.name
            })
        
        db.session.commit()
        
        return jsonify({
            'message': f'Column type updated successfully. Models regenerated for {len(updated_projects)} project(s).',
            'updated_projects': updated_projects,
            'model_file_path': mapping.model_file_path if mapping else None
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error updating column type: {str(e)}'}), 500


@tables_bp.route('/model/<int:connection_id>/<path:table_name>', methods=['GET'])
@token_required
def get_model_code(user, connection_id, table_name):
    """Get SQLAlchemy model code for a table"""
    # Verify connection belongs to user
    connection = DatabaseConnection.query.filter_by(
        id=connection_id,
        user_id=user.id
    ).first()
    
    if not connection:
        return jsonify({'message': 'Connection not found'}), 404
    
    # Get mapping
    mapping = TableModelMapping.query.filter_by(
        connection_id=connection_id,
        table_name=table_name,
        user_id=user.id
    ).first()
    
    if not mapping:
        return jsonify({'message': 'Model file not found for this table'}), 404
    
    try:
        # Read model file
        model_path = Path(mapping.model_file_path)
        if not model_path.exists():
            return jsonify({'message': 'Model file does not exist'}), 404
        
        with open(model_path, 'r', encoding='utf-8') as f:
            model_code = f.read()
        
        return jsonify({
            'model_code': model_code,
            'file_path': str(model_path),
            'table_name': table_name,
            'connection_name': connection.name
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error reading model file: {str(e)}'}), 500


@tables_bp.route('/data-types', methods=['GET'])
@token_required
def get_data_types(user):
    """Get list of available data types (similar to DBeaver)"""
    data_types = [
        {'value': 'Integer', 'label': 'INTEGER', 'category': 'Numeric'},
        {'value': 'BigInteger', 'label': 'BIGINT', 'category': 'Numeric'},
        {'value': 'SmallInteger', 'label': 'SMALLINT', 'category': 'Numeric'},
        {'value': 'String', 'label': 'VARCHAR/CHAR', 'category': 'String'},
        {'value': 'Text', 'label': 'TEXT', 'category': 'String'},
        {'value': 'DateTime', 'label': 'DATETIME', 'category': 'Date/Time'},
        {'value': 'Date', 'label': 'DATE', 'category': 'Date/Time'},
        {'value': 'Time', 'label': 'TIME', 'category': 'Date/Time'},
        {'value': 'Float', 'label': 'FLOAT', 'category': 'Numeric'},
        {'value': 'Numeric', 'label': 'DECIMAL/NUMERIC', 'category': 'Numeric'},
        {'value': 'Boolean', 'label': 'BOOLEAN', 'category': 'Boolean'},
        {'value': 'LargeBinary', 'label': 'BLOB', 'category': 'Binary'},
        {'value': 'JSON', 'label': 'JSON', 'category': 'JSON'}
    ]
    
    return jsonify({'data_types': data_types}), 200


