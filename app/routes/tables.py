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
                # Use begin() to ensure transaction is committed
                with engine.begin() as conn:
                    if primary_key:
                        # Add primary key constraint
                        # First, remove existing primary key if exists
                        if current_primary_keys:
                            alter_sql = f"ALTER TABLE `{table_name}` DROP PRIMARY KEY"
                            try:
                                conn.execute(text(alter_sql))
                                print(f"[TABLES] Dropped existing primary key from {table_name}")
                            except Exception as e:
                                print(f"Warning: Could not drop primary key: {e}")
                        
                        # Add new primary key
                        alter_sql = f"ALTER TABLE `{table_name}` ADD PRIMARY KEY (`{column_name}`)"
                        conn.execute(text(alter_sql))
                        print(f"[TABLES] Added primary key to column {column_name} in {table_name}")
                    else:
                        # Remove primary key constraint
                        if was_primary_key:
                            alter_sql = f"ALTER TABLE `{table_name}` DROP PRIMARY KEY"
                            try:
                                conn.execute(text(alter_sql))
                                print(f"[TABLES] Removed primary key from column {column_name} in {table_name}")
                            except Exception as e:
                                print(f"Warning: Could not drop primary key: {e}")
                    # Transaction is automatically committed when exiting 'with' block
            # Note: SQLite doesn't support ALTER TABLE for primary keys easily
        
        # Map form type to database-specific type
        # The form sends types like 'VARCHAR(255)', 'TEXT', 'INT', 'BOOLEAN', etc.
        # We need to map these to actual database types
        if connection.db_type.lower() in ['mariadb', 'mysql']:
            # Direct mapping - form already sends correct MySQL types
            if new_type.upper() == 'BOOLEAN':
                db_type = 'TINYINT(1)'  # Use TINYINT(1) for MySQL/MariaDB
            elif new_type.upper().startswith('VARCHAR'):
                db_type = new_type  # Keep as is (e.g., VARCHAR(255))
            elif new_type.upper().startswith('DECIMAL'):
                db_type = new_type  # Keep as is (e.g., DECIMAL(10,2))
            elif new_type.upper().startswith('TINYINT'):
                db_type = new_type  # Keep as is
            else:
                # Map common types
                type_mapping = {
                    'INT': 'INT',
                    'BIGINT': 'BIGINT',
                    'TEXT': 'TEXT',
                    'DATETIME': 'DATETIME',
                    'DATE': 'DATE',
                    'TIMESTAMP': 'TIMESTAMP',
                    'FLOAT': 'FLOAT',
                    'DOUBLE': 'DOUBLE'
                }
                db_type = type_mapping.get(new_type.upper(), new_type)
        else:
            # SQLite - use similar mapping
            if new_type.upper() == 'BOOLEAN':
                db_type = 'BOOLEAN'
            elif new_type.upper().startswith('VARCHAR'):
                db_type = 'TEXT'  # SQLite doesn't have VARCHAR, use TEXT
            elif new_type.upper().startswith('DECIMAL'):
                db_type = 'REAL'  # SQLite uses REAL for decimals
            else:
                db_type = new_type
        
        # Alter column type in database (SQLite/MariaDB specific)
        if connection.db_type.lower() == 'sqlite':
            # SQLite has limited ALTER TABLE support - we need to recreate the table
            print(f"[TABLES] SQLite detected - recreating table to change column type")
            try:
                with engine.begin() as conn:
                    print(f"[TABLES] ===== Starting SQLite table recreation ======")
                    print(f"[TABLES] Table: {table_name}, Column: {column_name}")
                    print(f"[TABLES] New type: {new_type}, DB type: {db_type}")
                    
                    # Get current table structure
                    inspector = inspect(engine)
                    current_cols = inspector.get_columns(table_name)
                    current_col = next((c for c in current_cols if c['name'] == column_name), None)
                    
                    if not current_col:
                        raise Exception(f"Column {column_name} not found in table {table_name}")
                    
                    # Get primary keys
                    pk_constraint = inspector.get_pk_constraint(table_name)
                    primary_keys = pk_constraint.get('constrained_columns', [])
                    
                    # Get all column names for SELECT
                    all_column_names = [col['name'] for col in current_cols]
                    
                    # Build new column definitions
                    new_column_defs = []
                    for col in current_cols:
                        col_name = col['name']
                        if col_name == column_name:
                            # Use new type
                            col_type = db_type
                            col_nullable = nullable
                            col_pk = primary_key
                        else:
                            # Keep existing type and properties
                            col_type = str(col['type'])
                            col_nullable = col.get('nullable', True)
                            col_pk = col_name in primary_keys
                        
                        col_def = f"`{col_name}` {col_type}"
                        if col_pk:
                            col_def += " PRIMARY KEY"
                        elif not col_nullable:
                            col_def += " NOT NULL"
                        new_column_defs.append(col_def)
                    
                    # Create temporary table name
                    temp_table_name = f"{table_name}_temp_{int(datetime.utcnow().timestamp())}"
                    
                    # Step 1: Create new table with updated structure
                    create_sql = f"CREATE TABLE `{temp_table_name}` ({', '.join(new_column_defs)})"
                    print(f"[TABLES] Creating temporary table: {create_sql}")
                    conn.execute(text(create_sql))
                    
                    # Step 2: Copy data from old table to new table
                    column_list = ', '.join([f"`{col}`" for col in all_column_names])
                    copy_sql = f"INSERT INTO `{temp_table_name}` ({column_list}) SELECT {column_list} FROM `{table_name}`"
                    print(f"[TABLES] Copying data: {copy_sql}")
                    conn.execute(text(copy_sql))
                    
                    # Step 3: Drop old table
                    drop_sql = f"DROP TABLE `{table_name}`"
                    print(f"[TABLES] Dropping old table: {drop_sql}")
                    conn.execute(text(drop_sql))
                    
                    # Step 4: Rename new table to original name
                    rename_sql = f"ALTER TABLE `{temp_table_name}` RENAME TO `{table_name}`"
                    print(f"[TABLES] Renaming table: {rename_sql}")
                    conn.execute(text(rename_sql))
                    
                    print(f"[TABLES] ===== SQLite table recreation completed ======")
            except Exception as e:
                import traceback
                print(f"[TABLES] ERROR recreating SQLite table: {str(e)}")
                print(traceback.format_exc())
                raise Exception(f"Failed to recreate SQLite table: {str(e)}")
        elif connection.db_type.lower() in ['mariadb', 'mysql']:
            # Use begin() to start a transaction
            try:
                with engine.begin() as conn:
                    print(f"[TABLES] ===== Starting ALTER TABLE ======")
                    print(f"[TABLES] Table: {table_name}, Column: {column_name}")
                    print(f"[TABLES] New type from form: {new_type}")
                    print(f"[TABLES] Mapped DB type: {db_type}")
                    print(f"[TABLES] Nullable: {nullable}, Primary Key: {primary_key}")
                    
                    # Get current column type to see if we need to convert data
                    inspector = inspect(engine)
                    current_cols = inspector.get_columns(table_name)
                    current_col = next((c for c in current_cols if c['name'] == column_name), None)
                    
                    if not current_col:
                        raise Exception(f"Column {column_name} not found in table {table_name}")
                    
                    current_type = str(current_col['type']).upper()
                    print(f"[TABLES] Current column type in DB: {current_type}")
                    
                    # Build ALTER TABLE statement
                    if new_type.upper() == 'BOOLEAN' or 'TINYINT(1)' in db_type.upper():
                        # Boolean type - use TINYINT(1)
                        alter_sql = f"ALTER TABLE `{table_name}` MODIFY COLUMN `{column_name}` TINYINT(1)"
                        if not nullable:
                            alter_sql += " NOT NULL"
                    else:
                        # For non-Boolean types, use the mapped db_type
                        alter_sql = f"ALTER TABLE `{table_name}` MODIFY COLUMN `{column_name}` {db_type}"
                        if not nullable:
                            alter_sql += " NOT NULL"
                    
                    print(f"[TABLES] SQL to execute: {alter_sql}")
                    
                    # Execute ALTER TABLE
                    result = conn.execute(text(alter_sql))
                    print(f"[TABLES] ALTER TABLE executed successfully")
                    print(f"[TABLES] Result: {result}")
                    
                    # If converting to Boolean from string/text, convert data
                    if new_type.upper() == 'BOOLEAN' or 'TINYINT(1)' in db_type.upper():
                        if 'VARCHAR' in current_type or 'TEXT' in current_type or 'CHAR' in current_type:
                            # Update existing data: convert 'true'/'false' strings to 1/0
                            update_sql = f"""
                                UPDATE `{table_name}` 
                                SET `{column_name}` = CASE 
                                    WHEN LOWER(TRIM(CAST(`{column_name}` AS CHAR))) = 'true' THEN 1
                                    WHEN LOWER(TRIM(CAST(`{column_name}` AS CHAR))) = 'false' THEN 0
                                    WHEN CAST(`{column_name}` AS CHAR) = '1' THEN 1
                                    WHEN CAST(`{column_name}` AS CHAR) = '0' THEN 0
                                    ELSE 0
                                END
                            """
                            try:
                                print(f"[TABLES] Executing data conversion: {update_sql}")
                                update_result = conn.execute(text(update_sql))
                                print(f"[TABLES] Data conversion executed. Rows affected: {update_result.rowcount if hasattr(update_result, 'rowcount') else 'N/A'}")
                            except Exception as e:
                                print(f"[TABLES] Warning: Could not convert existing data: {e}")
                                import traceback
                                print(traceback.format_exc())
                    
                    # Transaction is automatically committed when exiting 'with' block
                    print(f"[TABLES] ===== ALTER TABLE transaction completed ======")
                    
            except Exception as e:
                import traceback
                print(f"[TABLES] ERROR executing ALTER TABLE: {str(e)}")
                print(traceback.format_exc())
                raise Exception(f"Failed to execute ALTER TABLE: {str(e)}")
        else:
            print(f"[TABLES] Unsupported database type: {connection.db_type}")
        
        # IMPORTANT: Create a new engine connection to ensure we get fresh data
        # The inspector may cache column information, so we need to refresh it
        print(f"[TABLES] ===== Refreshing column information from database ======")
        
        # Close the old engine to force a fresh connection
        try:
            engine.dispose()
        except:
            pass
        
        # Create a completely new engine
        fresh_engine = DatabaseService.get_engine(decrypted_config, already_decrypted=True)
        
        # Get updated columns (refresh after potential primary key changes)
        # This ensures we have the latest column information from the database
        columns = DatabaseService.get_table_columns(fresh_engine, table_name)
        updated_primary_keys = DatabaseService.get_primary_keys(fresh_engine, table_name)
        
        print(f"[TABLES] Retrieved {len(columns)} columns from database")
        found_updated_column = False
        for col in columns:
            if col['name'] == column_name:
                found_updated_column = True
                print(f"[TABLES] ===== UPDATED COLUMN INFO ======")
                print(f"[TABLES] Name: {col['name']}")
                print(f"[TABLES] Type: {col['type']}")
                print(f"[TABLES] Nullable: {col['nullable']}")
                print(f"[TABLES] Primary Key: {col['primary_key']}")
                print(f"[TABLES] =================================")
        
        if not found_updated_column:
            print(f"[TABLES] WARNING: Column {column_name} not found in refreshed columns!")
            raise Exception(f"Column {column_name} not found after update")
        
        # Verify column information matches what we expect
        # The columns already contain the updated info from database query above
        for col in columns:
            if col['name'] == column_name:
                # Ensure primary key status is correct (from database)
                col['primary_key'] = col['name'] in updated_primary_keys
                print(f"[TABLES] Final column info - Name: {col['name']}, Type: {col['type']}, Nullable: {col['nullable']}, Primary Key: {col['primary_key']}")
        
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
        
        # Always generate and save model file, even if no projects exist
        # Use connection name + table name as fallback if no projects
        if projects:
            # Generate model for each project (they may have different names)
            for project in projects:
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
            
            # Use first project name for mapping
            project_name_for_model = projects[0].name
        else:
            # No projects - use connection name + table name
            project_name_for_model = f"{connection.name}_{table_name}"
        
        # Always generate model code (even if no projects)
        # This ensures the model file always exists and is up-to-date
        try:
            model_code = TableMapper.generate_model_code(table_name, columns, decrypted_config)
            model_path = TableMapper.save_model_file(
                project_name_for_model,
                table_name,
                model_code,
                base_path
            )
            
            print(f"[TABLES] Model file saved/updated: {model_path}")
            
            # Verify file was created
            if not model_path.exists():
                raise Exception(f"Model file was not created at {model_path}")
            
        except Exception as e:
            import traceback
            print(f"[TABLES] Error generating/saving model file: {str(e)}")
            print(traceback.format_exc())
            # Still try to continue, but log the error
            model_path = None
        
        # Update or create mapping (always ensure mapping exists)
        if not mapping:
            if model_path:
                mapping = TableModelMapping(
                    connection_id=connection_id,
                    table_name=table_name,
                    model_file_path=str(model_path),
                    user_id=user.id
                )
                db.session.add(mapping)
                print(f"[TABLES] Created new TableModelMapping for {table_name}")
            else:
                print(f"[TABLES] Warning: Could not create mapping - model file was not created")
        else:
            if model_path:
                mapping.model_file_path = str(model_path)
                mapping.updated_at = datetime.utcnow()
                print(f"[TABLES] Updated TableModelMapping for {table_name}")
            else:
                print(f"[TABLES] Warning: Could not update mapping - model file was not created")
        
        # Commit all database changes (including TableModelMapping)
        try:
            db.session.commit()
            print(f"[TABLES] Database changes committed successfully")
        except Exception as e:
            db.session.rollback()
            import traceback
            print(f"[TABLES] Error committing database changes: {str(e)}")
            print(traceback.format_exc())
            raise
        
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


