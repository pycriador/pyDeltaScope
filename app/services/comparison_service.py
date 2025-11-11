import pandas as pd
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from app.services.database import DatabaseService
from app.models.comparison import Comparison, ComparisonResult
from app.models.change_log import ChangeLog
from app import db
import requests
from flask import current_app


class ComparisonService:
    """Service for comparing tables and tracking changes"""
    
    @staticmethod
    def compare_tables(
        source_config: Dict,
        target_config: Dict,
        source_table: str,
        target_table: str,
        primary_keys: List[str],
        key_mappings: Optional[Dict[str, str]] = None
    ) -> Tuple[pd.DataFrame, List[Dict]]:
        """
        Compare two tables and return differences
        
        Args:
            source_config: Source database configuration
            target_config: Target database configuration
            source_table: Source table name
            target_table: Target table name
            primary_keys: List of primary key column names in source table
            key_mappings: Dictionary mapping source column names to target column names
                        e.g., {'user_id': 'id_user', 'name': 'nome'}
        
        Returns:
            Tuple of (differences DataFrame, list of change dictionaries)
        """
        key_mappings = key_mappings or {}
        
        source_engine = DatabaseService.get_engine(source_config, already_decrypted=True)
        target_engine = DatabaseService.get_engine(target_config, already_decrypted=True)
        
        # Get data from both tables
        source_df = DatabaseService.get_table_data(source_engine, source_table)
        target_df = DatabaseService.get_table_data(target_engine, target_table)
        
        # Ensure primary keys exist
        if not primary_keys:
            # Try to infer primary keys
            source_pks = DatabaseService.get_primary_keys(source_engine, source_table)
            if source_pks:
                primary_keys = source_pks
            else:
                # Use all columns if no PK found
                primary_keys = list(source_df.columns)
        
        # Map target primary keys if mapping provided
        target_primary_keys = []
        for pk in primary_keys:
            if pk in key_mappings:
                target_primary_keys.append(key_mappings[pk])
            else:
                # If no mapping, assume same name
                target_primary_keys.append(pk)
        
        # Verify all target primary keys exist
        missing_keys = [pk for pk in target_primary_keys if pk not in target_df.columns]
        if missing_keys:
            raise ValueError(f"Target table missing primary key columns: {missing_keys}")
        
        # Rename target columns to match source for comparison
        target_df_mapped = target_df.copy()
        reverse_mapping = {v: k for k, v in key_mappings.items()}
        for target_col in target_df_mapped.columns:
            if target_col in reverse_mapping:
                target_df_mapped.rename(columns={target_col: reverse_mapping[target_col]}, inplace=True)
        
        # Set index for comparison using source column names
        source_df_indexed = source_df.set_index(primary_keys)
        target_df_indexed = target_df_mapped.set_index(primary_keys)
        
        # Find differences
        differences = []
        
        # Find records in source but not in target (added)
        source_only = source_df_indexed.index.difference(target_df_indexed.index)
        for idx in source_only:
            record = source_df_indexed.loc[idx]
            for col in source_df.columns:
                if col not in primary_keys:
                    differences.append({
                        'record_id': str(idx) if isinstance(idx, tuple) else idx,
                        'field_name': col,
                        'source_value': str(record[col]) if pd.notna(record[col]) else None,
                        'target_value': None,
                        'change_type': 'added'
                    })
        
        # Find records in target but not in source (deleted)
        target_only = target_df_indexed.index.difference(source_df_indexed.index)
        for idx in target_only:
            record = target_df_indexed.loc[idx]
            # Use columns from mapped target dataframe
            for col in target_df_indexed.columns:
                if col not in primary_keys:
                    differences.append({
                        'record_id': str(idx) if isinstance(idx, tuple) else idx,
                        'field_name': col,
                        'source_value': None,
                        'target_value': str(record[col]) if pd.notna(record[col]) else None,
                        'change_type': 'deleted'
                    })
        
        # Find modified records
        common_index = source_df_indexed.index.intersection(target_df_indexed.index)
        for idx in common_index:
            source_record = source_df_indexed.loc[idx]
            target_record = target_df_indexed.loc[idx]
            
            # Compare all columns that exist in both dataframes
            for col in source_df.columns:
                if col not in primary_keys:
                    # Check if column exists in target (after mapping)
                    if col in target_df_indexed.columns:
                        source_val = source_record[col] if pd.notna(source_record[col]) else None
                        target_val = target_record[col] if pd.notna(target_record[col]) else None
                        
                        if str(source_val) != str(target_val):
                            differences.append({
                                'record_id': str(idx) if isinstance(idx, tuple) else idx,
                                'field_name': col,
                                'source_value': str(source_val) if source_val is not None else None,
                                'target_value': str(target_val) if target_val is not None else None,
                                'change_type': 'modified'
                            })
                    else:
                        # Column exists in source but not in target (after mapping)
                        source_val = source_record[col] if pd.notna(source_record[col]) else None
                        differences.append({
                            'record_id': str(idx) if isinstance(idx, tuple) else idx,
                            'field_name': col,
                            'source_value': str(source_val) if source_val is not None else None,
                            'target_value': None,
                            'change_type': 'added'
                        })
        
        differences_df = pd.DataFrame(differences)
        
        return differences_df, differences
    
    @staticmethod
    def save_comparison_results(
        project_id: int,
        differences: List[Dict],
        metadata: Optional[Dict] = None
    ) -> Comparison:
        """Save comparison results to database"""
        comparison = Comparison(
            project_id=project_id,
            status='completed',
            total_differences=len(differences),
            comparison_metadata=metadata or {}
        )
        db.session.add(comparison)
        db.session.flush()
        
        # Save individual results
        for diff in differences:
            result = ComparisonResult(
                comparison_id=comparison.id,
                record_id=diff.get('record_id'),
                field_name=diff.get('field_name'),
                source_value=diff.get('source_value'),
                target_value=diff.get('target_value'),
                change_type=diff.get('change_type')
            )
            db.session.add(result)
            
            # Create change log entry
            change_log = ChangeLog(
                project_id=project_id,
                comparison_id=comparison.id,
                record_id=diff.get('record_id'),
                field_name=diff.get('field_name'),
                old_value=diff.get('target_value'),
                new_value=diff.get('source_value'),
                change_type=diff.get('change_type')
            )
            db.session.add(change_log)
        
        db.session.commit()
        return comparison
    
    @staticmethod
    def send_changes_to_api(change_logs: List[ChangeLog]) -> Dict:
        """Send change logs to external API"""
        endpoint = current_app.config.get('EXTERNAL_API_ENDPOINT')
        token = current_app.config.get('EXTERNAL_API_TOKEN')
        
        if not endpoint:
            return {'success': False, 'error': 'External API endpoint not configured'}
        
        results = {
            'success': [],
            'failed': []
        }
        
        for change_log in change_logs:
            if change_log.sent_to_api:
                continue
            
            payload = {
                'id': change_log.id,
                'project_id': change_log.project_id,
                'record_id': change_log.record_id,
                'field_name': change_log.field_name,
                'old_value': change_log.old_value,
                'new_value': change_log.new_value,
                'change_type': change_log.change_type,
                'detected_at': change_log.detected_at.isoformat() if change_log.detected_at else None
            }
            
            headers = {
                'Content-Type': 'application/json'
            }
            
            if token:
                headers['Authorization'] = f'Bearer {token}'
            
            try:
                response = requests.post(
                    endpoint,
                    json=payload,
                    headers=headers,
                    timeout=30
                )
                
                change_log.sent_to_api = True
                change_log.sent_at = datetime.utcnow()
                change_log.api_response = {
                    'status_code': response.status_code,
                    'response': response.text[:500]  # Limit response size
                }
                
                if response.status_code in [200, 201]:
                    results['success'].append(change_log.id)
                else:
                    results['failed'].append({
                        'id': change_log.id,
                        'status_code': response.status_code,
                        'error': response.text[:200]
                    })
            
            except Exception as e:
                results['failed'].append({
                    'id': change_log.id,
                    'error': str(e)
                })
        
        db.session.commit()
        return results


