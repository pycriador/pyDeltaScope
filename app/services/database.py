from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine
from typing import Dict, List, Optional
import pandas as pd
from urllib.parse import quote_plus
from app.utils.encryption import decrypt_db_config


class DatabaseService:
    """Service for database operations"""
    
    @staticmethod
    def create_connection_string(db_config: Dict) -> str:
        """Create SQLAlchemy connection string from config"""
        db_type = db_config.get('type', 'sqlite').lower()
        
        if db_type == 'sqlite':
            return f"sqlite:///{db_config.get('path', 'database.db')}"
        elif db_type in ['mariadb', 'mysql']:
            host = db_config.get('host', 'localhost')
            port = db_config.get('port', '3306')
            user = db_config.get('user', 'root')
            password = db_config.get('password', '') or ''
            database = db_config.get('database', '')
            
            # URL encode password to handle special characters
            user_encoded = quote_plus(str(user))
            password_encoded = quote_plus(str(password))
            host_encoded = quote_plus(str(host))
            database_encoded = quote_plus(str(database))
            
            return f"mysql+pymysql://{user_encoded}:{password_encoded}@{host_encoded}:{port}/{database_encoded}"
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
    
    @staticmethod
    def get_engine(db_config: Dict, already_decrypted: bool = False) -> Engine:
        """Get SQLAlchemy engine from config
        
        Args:
            db_config: Database configuration dictionary
            already_decrypted: If True, assumes password is already decrypted
        """
        # Only decrypt if not already decrypted
        if already_decrypted:
            decrypted_config = db_config.copy()
        else:
            decrypted_config = decrypt_db_config(db_config)
        
        connection_string = DatabaseService.create_connection_string(decrypted_config)
        return create_engine(connection_string)
    
    @staticmethod
    def get_tables(engine: Engine) -> List[str]:
        """Get list of table names from database"""
        inspector = inspect(engine)
        return inspector.get_table_names()
    
    @staticmethod
    def get_table_columns(engine: Engine, table_name: str) -> List[Dict]:
        """Get column information for a table"""
        inspector = inspect(engine)
        columns = inspector.get_columns(table_name)
        return [
            {
                'name': col['name'],
                'type': str(col['type']),
                'nullable': col.get('nullable', True),
                'primary_key': col.get('primary_key', False)
            }
            for col in columns
        ]
    
    @staticmethod
    def get_table_data(engine: Engine, table_name: str, limit: Optional[int] = None) -> pd.DataFrame:
        """Get data from a table as pandas DataFrame"""
        query = f"SELECT * FROM {table_name}"
        if limit:
            query += f" LIMIT {limit}"
        
        return pd.read_sql(query, engine)
    
    @staticmethod
    def get_table_row_count(engine: Engine, table_name: str) -> int:
        """Get row count for a table"""
        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            return result.scalar()
    
    @staticmethod
    def get_primary_keys(engine: Engine, table_name: str) -> List[str]:
        """Get primary key columns for a table"""
        inspector = inspect(engine)
        pk_constraint = inspector.get_pk_constraint(table_name)
        return pk_constraint.get('constrained_columns', [])


