from typing import Dict, List, Tuple, Optional
from sqlalchemy import create_engine, text, inspect
from app.services.database import DatabaseService
import pandas as pd
from app import db
from app.models.data_consistency import DataConsistencyConfig, DataConsistencyCheck, DataConsistencyResult
from datetime import datetime


class ConsistencyService:
    """Service for data consistency checks between different tables"""
    
    @staticmethod
    def check_consistency(config: DataConsistencyConfig) -> Tuple[DataConsistencyCheck, List[Dict]]:
        """
        Check data consistency between two tables based on configuration
        
        Args:
            config: DataConsistencyConfig with join mappings and comparison fields
            
        Returns:
            Tuple of (DataConsistencyCheck, list of inconsistency results)
        """
        # Create consistency check record
        check = DataConsistencyCheck(
            config_id=config.id,
            status='running',
            total_inconsistencies=0
        )
        db.session.add(check)
        db.session.flush()
        
        try:
            # Get database connections
            source_connection = config.source_connection
            target_connection = config.target_connection
            
            # Get decrypted configs
            source_config = source_connection.get_decrypted_config()
            source_config['type'] = source_connection.db_type
            
            target_config = target_connection.get_decrypted_config()
            target_config['type'] = target_connection.db_type
            
            # Create engines
            source_engine = DatabaseService.get_engine(source_config, already_decrypted=True)
            target_engine = DatabaseService.get_engine(target_config, already_decrypted=True)
            
            # Get join mappings and comparison fields
            join_mappings = config.join_mappings or {}
            comparison_fields = config.comparison_fields or []
            
            if not join_mappings:
                raise ValueError("No join mappings defined")
            
            if not comparison_fields:
                raise ValueError("No comparison fields defined")
            
            # Since tables are in different databases, we need to query them separately
            # and compare in memory using pandas
            
            # Build SELECT clause for source table
            source_select_fields = []
            for source_field in join_mappings.keys():
                source_select_fields.append(f"{source_field}")
            for field_map in comparison_fields:
                source_select_fields.append(field_map['source_field'])
            
            source_select = ", ".join(source_select_fields)
            
            # Query source table
            source_sql = f"SELECT {source_select} FROM {config.source_table}"
            source_df = pd.read_sql(text(source_sql), source_engine)
            
            # Build SELECT clause for target table
            target_select_fields = []
            for target_field in join_mappings.values():
                target_select_fields.append(f"{target_field}")
            for field_map in comparison_fields:
                target_select_fields.append(field_map['target_field'])
            
            target_select = ", ".join(target_select_fields)
            
            # Query target table
            target_sql = f"SELECT {target_select} FROM {config.target_table}"
            target_df = pd.read_sql(text(target_sql), target_engine)
            
            # Create a composite key for joining dataframes
            # Build key columns for source
            source_key_cols = list(join_mappings.keys())
            # Build key columns for target (mapped values)
            target_key_cols = list(join_mappings.values())
            
            # Rename target columns to match source for easier comparison
            target_df_renamed = target_df.copy()
            rename_map = {}
            
            # Rename join key columns
            for source_field, target_field in join_mappings.items():
                rename_map[target_field] = source_field
            
            # Rename comparison fields to match source field names
            # This way, merge will add suffixes _source and _target correctly
            for field_map in comparison_fields:
                source_field = field_map['source_field']
                target_field = field_map['target_field']
                rename_map[target_field] = source_field
            
            target_df_renamed = target_df_renamed.rename(columns=rename_map)
            
            # For merge, we need to ensure both dataframes have the same key column names
            # The target_df_renamed already has renamed join keys matching source
            
            # Merge dataframes on join keys
            # Only merge on the key columns (which are now renamed to match)
            merged_df = source_df.merge(
                target_df_renamed,
                on=source_key_cols,
                how='outer',
                suffixes=('_source', '_target'),
                indicator=True
            )
            
            inconsistencies = []
            
            # Process merged results
            for idx, row in merged_df.iterrows():
                # Build join key values
                join_key_values = {}
                for source_field in source_key_cols:
                    value = row.get(source_field)
                    if pd.notna(value):
                        join_key_values[source_field] = str(value)
                    else:
                        # Try to get from target (for right_only cases)
                        value = row.get(f"{source_field}_target")
                        if pd.notna(value):
                            join_key_values[source_field] = str(value)
                        else:
                            join_key_values[source_field] = 'N/A'
                
                # Check merge indicator
                merge_indicator = row.get('_merge', 'both')
                
                # Check each comparison field
                for field_map in comparison_fields:
                    source_field = field_map['source_field']
                    source_col = f"{source_field}_source"
                    target_col = f"{source_field}_target"
                    
                    source_value = row.get(source_col)
                    target_value = row.get(target_col)
                    
                    # Determine inconsistency type
                    if merge_indicator == 'left_only':
                        # Record exists only in source - add inconsistency for this field
                        inconsistency_type = 'missing_in_target'
                        inconsistencies.append({
                            'join_key_values': join_key_values,
                            'field_name': source_field,
                            'source_value': str(source_value) if pd.notna(source_value) else None,
                            'target_value': None,
                            'inconsistency_type': inconsistency_type
                        })
                    elif merge_indicator == 'right_only':
                        # Record exists only in target - add inconsistency for this field
                        inconsistency_type = 'missing_in_source'
                        inconsistencies.append({
                            'join_key_values': join_key_values,
                            'field_name': source_field,
                            'source_value': None,
                            'target_value': str(target_value) if pd.notna(target_value) else None,
                            'inconsistency_type': inconsistency_type
                        })
                    elif merge_indicator == 'both':
                        # Both records exist, check if values match
                        source_str = str(source_value) if pd.notna(source_value) else None
                        target_str = str(target_value) if pd.notna(target_value) else None
                        
                        if source_str != target_str:
                            inconsistency_type = 'value_mismatch'
                            inconsistencies.append({
                                'join_key_values': join_key_values,
                                'field_name': source_field,
                                'source_value': source_str,
                                'target_value': target_str,
                                'inconsistency_type': inconsistency_type
                            })
            
            # Save inconsistencies
            check.status = 'completed'
            check.total_inconsistencies = len(inconsistencies)
            
            for inconsistency in inconsistencies:
                result = DataConsistencyResult(
                    check_id=check.id,
                    join_key_values=inconsistency['join_key_values'],
                    field_name=inconsistency['field_name'],
                    source_value=inconsistency['source_value'],
                    target_value=inconsistency['target_value'],
                    inconsistency_type=inconsistency['inconsistency_type']
                )
                db.session.add(result)
            
            db.session.commit()
            
            return check, inconsistencies
            
        except Exception as e:
            check.status = 'failed'
            check.check_metadata = {'error': str(e)}
            db.session.commit()
            raise e

