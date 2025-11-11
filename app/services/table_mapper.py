from pathlib import Path
from typing import Dict, List
from app.services.database import DatabaseService


class TableMapper:
    """Service for mapping database tables to SQLAlchemy models"""
    
    @staticmethod
    def generate_model_code(table_name: str, columns: List[Dict], db_config: Dict) -> str:
        """Generate SQLAlchemy model code for a table"""
        model_name = TableMapper._to_camel_case(table_name)
        
        lines = [
            "from datetime import datetime",
            "from app import db",
            "",
            "",
            f"class {model_name}(db.Model):",
            f'    """Model for table {table_name}"""',
            f'    __tablename__ = "{table_name}"',
            ""
        ]
        
        # Add columns
        for col in columns:
            col_name = col['name']
            # Get type from column - handle both string and dict formats
            col_type_str = str(col.get('type', 'String'))
            col_type = TableMapper._map_column_type(col_type_str)
            nullable = col.get('nullable', True)
            primary_key = col.get('primary_key', False)
            
            # Handle spaces in column names - use underscore and add alias
            python_col_name = col_name
            has_space = ' ' in col_name
            if has_space:
                python_col_name = col_name.replace(' ', '_')
            
            # Build column definition
            col_def = f"    {python_col_name} = db.Column(db.{col_type}"
            
            # Add column name parameter if it has spaces (to keep original name)
            if has_space:
                col_def += f', name="{col_name}"'
            
            if not nullable:
                col_def += ", nullable=False"
            if primary_key:
                col_def += ", primary_key=True"
            col_def += ")"
            
            lines.append(col_def)
        
        lines.extend([
            "",
            "    def to_dict(self):",
            '        """Convert model to dictionary"""',
            "        return {",
        ])
        
        for col in columns:
            col_name = col['name']
            python_col_name = col_name
            if ' ' in col_name:
                python_col_name = col_name.replace(' ', '_')
            lines.append(f'            "{col_name}": self.{python_col_name},')
        
        lines.extend([
            "        }",
            "",
            f'    def __repr__(self):',
            f'        return f"<{model_name} {{self.id}}>"',
            ""
        ])
        
        return "\n".join(lines)
    
    @staticmethod
    def _to_camel_case(snake_str: str) -> str:
        """Convert snake_case to CamelCase"""
        components = snake_str.split('_')
        return ''.join(x.capitalize() for x in components)
    
    @staticmethod
    def _map_column_type(db_type: str) -> str:
        """Map database type to SQLAlchemy type"""
        db_type_lower = db_type.lower()
        
        type_mapping = {
            'integer': 'Integer',
            'int': 'Integer',
            'bigint': 'BigInteger',
            'smallint': 'SmallInteger',
            'varchar': 'String',
            'char': 'String',
            'text': 'Text',
            'datetime': 'DateTime',
            'date': 'Date',
            'time': 'Time',
            'timestamp': 'DateTime',
            'float': 'Float',
            'double': 'Float',
            'decimal': 'Numeric',
            'numeric': 'Numeric',
            'boolean': 'Boolean',
            'bool': 'Boolean',
            'json': 'JSON',
            'blob': 'LargeBinary',
        }
        
        for key, value in type_mapping.items():
            if key in db_type_lower:
                return value
        
        return 'String'  # Default
    
    @staticmethod
    def save_model_file(project_name: str, table_name: str, model_code: str, base_path: Path) -> Path:
        """Save generated model to file"""
        models_dir = base_path / 'app' / 'models' / 'generated'
        models_dir.mkdir(parents=True, exist_ok=True)
        
        # Sanitize project name and table name for filename
        safe_project = TableMapper._sanitize_filename(project_name)
        safe_table = TableMapper._sanitize_filename(table_name)
        filename = f"{safe_project}_{safe_table}_model.py"
        
        file_path = models_dir / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(model_code)
        
        return file_path
    
    @staticmethod
    def _sanitize_filename(name: str) -> str:
        """Sanitize string for use in filename"""
        return "".join(c for c in name if c.isalnum() or c in ('_', '-')).strip()


