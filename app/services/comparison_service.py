import pandas as pd
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from app.services.database import DatabaseService
from app.models.comparison import Comparison, ComparisonResult
from app.models.change_log import ChangeLog
from app import db
import requests
from flask import current_app
import sys


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
        
        # Ensure key_mappings is a dict
        if not isinstance(key_mappings, dict):
            print(f"[COMPARISON] WARNING: key_mappings is not a dict, converting. Type: {type(key_mappings)}, Value: {key_mappings}", flush=True)
            if isinstance(key_mappings, str):
                try:
                    import json
                    key_mappings = json.loads(key_mappings)
                except:
                    key_mappings = {}
            else:
                key_mappings = {}
        
        print(f"[COMPARISON] Starting comparison with key_mappings: {key_mappings}", flush=True)
        print(f"[COMPARISON] Key mappings type: {type(key_mappings)}, length: {len(key_mappings)}", flush=True)
        
        source_engine = DatabaseService.get_engine(source_config, already_decrypted=True)
        target_engine = DatabaseService.get_engine(target_config, already_decrypted=True)
        
        # Get data from both tables
        source_df = DatabaseService.get_table_data(source_engine, source_table)
        target_df = DatabaseService.get_table_data(target_engine, target_table)
        
        print(f"[COMPARISON] Source table rows: {len(source_df)}, columns: {list(source_df.columns)}", flush=True)
        print(f"[COMPARISON] Target table rows: {len(target_df)}, columns: {list(target_df.columns)}", flush=True)
        
        # Ensure primary keys exist
        if not primary_keys:
            # Try to infer primary keys
            source_pks = DatabaseService.get_primary_keys(source_engine, source_table)
            if source_pks:
                primary_keys = source_pks
                print(f"[COMPARISON] Inferred primary keys from database: {primary_keys}", flush=True)
            else:
                # Try common primary key names
                common_pk_names = ['id', 'ID', 'Id', '_id', 'pk_id', 'primary_key']
                found_pk = None
                for pk_name in common_pk_names:
                    if pk_name in source_df.columns:
                        found_pk = pk_name
                        break
                
                if found_pk:
                    primary_keys = [found_pk]
                    print(f"[COMPARISON] No PK found in DB, using common PK name: {primary_keys}", flush=True)
                else:
                    # Last resort: use all columns (but warn)
                    primary_keys = list(source_df.columns)
                    print(f"[COMPARISON] WARNING: No PK found and no common PK name found. Using ALL columns as PK: {primary_keys}", flush=True)
        
        print(f"[COMPARISON] Primary keys: {primary_keys}", flush=True)
        print(f"[COMPARISON] Key mappings: {key_mappings}", flush=True)
        print(f"[COMPARISON] Key mappings length: {len(key_mappings) if isinstance(key_mappings, dict) else 0}", flush=True)
        
        # Map target primary keys if mapping provided
        target_primary_keys = []
        for pk in primary_keys:
            if pk in key_mappings:
                mapped_pk = key_mappings[pk]
                target_primary_keys.append(mapped_pk)
                print(f"[COMPARISON] Primary key '{pk}' mapped to '{mapped_pk}'", flush=True)
            else:
                # If no mapping, assume same name
                target_primary_keys.append(pk)
                print(f"[COMPARISON] Primary key '{pk}' has no mapping, using same name", flush=True)
        
        print(f"[COMPARISON] Target primary keys (mapped): {target_primary_keys}", flush=True)
        
        # Verify all target primary keys exist
        missing_keys = [pk for pk in target_primary_keys if pk not in target_df.columns]
        if missing_keys:
            print(f"[COMPARISON] ERROR: Target table missing primary key columns: {missing_keys}", flush=True)
            print(f"[COMPARISON] Available target columns: {list(target_df.columns)}", flush=True)
            raise ValueError(f"Target table missing primary key columns: {missing_keys}")
        
        # Rename target columns to match source for comparison
        target_df_mapped = target_df.copy()
        reverse_mapping = {v: k for k, v in key_mappings.items()}
        print(f"[COMPARISON] Reverse mapping: {reverse_mapping}", flush=True)
        print(f"[COMPARISON] Target columns before mapping: {list(target_df_mapped.columns)}", flush=True)
        for target_col in target_df_mapped.columns:
            if target_col in reverse_mapping:
                source_col_name = reverse_mapping[target_col]
                target_df_mapped.rename(columns={target_col: source_col_name}, inplace=True)
                print(f"[COMPARISON] Renamed target column '{target_col}' to '{source_col_name}'", flush=True)
        
        print(f"[COMPARISON] Target columns after mapping: {list(target_df_mapped.columns)}", flush=True)
        
        # Set index for comparison using source column names
        print(f"[COMPARISON] Setting index on source using: {primary_keys}", flush=True)
        source_df_indexed = source_df.set_index(primary_keys)
        print(f"[COMPARISON] Setting index on target using: {primary_keys} (after mapping)", flush=True)
        target_df_indexed = target_df_mapped.set_index(primary_keys)
        
        print(f"[COMPARISON] Source indexed rows: {len(source_df_indexed)}", flush=True)
        print(f"[COMPARISON] Source index sample: {list(source_df_indexed.index[:3]) if len(source_df_indexed) > 0 else 'empty'}", flush=True)
        print(f"[COMPARISON] Target indexed rows: {len(target_df_indexed)}", flush=True)
        print(f"[COMPARISON] Target index sample: {list(target_df_indexed.index[:3]) if len(target_df_indexed) > 0 else 'empty'}", flush=True)
        
        # Helper function to format record_id
        def format_record_id(idx):
            """Format record ID for storage"""
            if isinstance(idx, tuple):
                # Join tuple values with separator
                return '|'.join(str(v) for v in idx)
            return str(idx) if idx is not None else None
        
        # Find differences
        differences = []
        
        # Find records in source but not in target (added)
        source_only = source_df_indexed.index.difference(target_df_indexed.index)
        print(f"[COMPARISON] Records only in source: {len(source_only)}", flush=True)
        for idx in source_only:
            record = source_df_indexed.loc[idx]
            for col in source_df.columns:
                if col not in primary_keys:
                    differences.append({
                        'record_id': format_record_id(idx),
                        'field_name': col,
                        'source_value': str(record[col]) if pd.notna(record[col]) else None,
                        'target_value': None,
                        'change_type': 'added'
                    })
        
        # Find records in target but not in source (deleted)
        target_only = target_df_indexed.index.difference(source_df_indexed.index)
        print(f"[COMPARISON] Records only in target: {len(target_only)}", flush=True)
        for idx in target_only:
            record = target_df_indexed.loc[idx]
            # Use columns from mapped target dataframe
            for col in target_df_indexed.columns:
                if col not in primary_keys:
                    differences.append({
                        'record_id': format_record_id(idx),
                        'field_name': col,
                        'source_value': None,
                        'target_value': str(record[col]) if pd.notna(record[col]) else None,
                        'change_type': 'deleted'
                    })
        
        # Find modified records
        common_index = source_df_indexed.index.intersection(target_df_indexed.index)
        print(f"[COMPARISON] Common records: {len(common_index)}", flush=True)
        modified_count = 0
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
                            modified_count += 1
                            differences.append({
                                'record_id': format_record_id(idx),
                                'field_name': col,
                                'source_value': str(source_val) if source_val is not None else None,
                                'target_value': str(target_val) if target_val is not None else None,
                                'change_type': 'modified'
                            })
                    else:
                        # Column exists in source but not in target (after mapping)
                        source_val = source_record[col] if pd.notna(source_record[col]) else None
                        differences.append({
                            'record_id': format_record_id(idx),
                            'field_name': col,
                            'source_value': str(source_val) if source_val is not None else None,
                            'target_value': None,
                            'change_type': 'added'
                        })
        
        print(f"[COMPARISON] Modified fields found: {modified_count}", flush=True)
        
        differences_df = pd.DataFrame(differences)
        
        print(f"[COMPARISON] Total differences found: {len(differences)}", flush=True)
        
        return differences_df, differences
    
    @staticmethod
    def save_comparison_results(
        project_id: int,
        differences: List[Dict],
        metadata: Optional[Dict] = None,
        user_id: Optional[int] = None
    ) -> Comparison:
        """Save comparison results to database"""
        print(f"[SAVE_RESULTS] Saving {len(differences)} differences for project {project_id}", flush=True)
        
        comparison = Comparison(
            project_id=project_id,
            status='completed',
            total_differences=len(differences),
            comparison_metadata=metadata or {}
        )
        if user_id:
            comparison.user_id = user_id
        db.session.add(comparison)
        db.session.flush()
        
        print(f"[SAVE_RESULTS] Comparison created with ID: {comparison.id}, total_differences: {comparison.total_differences}", flush=True)
        
        # Save individual results
        results_saved = 0
        if len(differences) == 0:
            print(f"[SAVE_RESULTS] WARNING: No differences to save! differences list is empty.", flush=True)
        else:
            print(f"[SAVE_RESULTS] Processing {len(differences)} differences...", flush=True)
            for i, diff in enumerate(differences):
                try:
                    record_id = str(diff.get('record_id')) if diff.get('record_id') is not None else None
                    field_name = diff.get('field_name')
                    source_value = str(diff.get('source_value')) if diff.get('source_value') is not None else None
                    target_value = str(diff.get('target_value')) if diff.get('target_value') is not None else None
                    change_type = diff.get('change_type')
                    
                    if i < 3:  # Log first 3 differences for debugging
                        print(f"[SAVE_RESULTS] Sample diff {i+1}: record_id={record_id}, field={field_name}, type={change_type}", flush=True)
                    
                    result = ComparisonResult(
                        comparison_id=comparison.id,
                        record_id=record_id,
                        field_name=field_name,
                        source_value=source_value,
                        target_value=target_value,
                        change_type=change_type
                    )
                    db.session.add(result)
                    results_saved += 1
                    
                    # Create change log entry
                    change_log = ChangeLog(
                        project_id=project_id,
                        comparison_id=comparison.id,
                        record_id=record_id,
                        field_name=field_name,
                        old_value=target_value,
                        new_value=source_value,
                        change_type=change_type
                    )
                    db.session.add(change_log)
                except Exception as e:
                    print(f"[SAVE_RESULTS] Error saving diff {i}: {str(e)}", flush=True)
                    import traceback
                    print(traceback.format_exc(), flush=True)
                    continue
        
        print(f"[SAVE_RESULTS] Added {results_saved} ComparisonResult records to session", flush=True)
        
        try:
            db.session.commit()
            print(f"[SAVE_RESULTS] Committed to database. Comparison ID: {comparison.id}", flush=True)
        except Exception as e:
            print(f"[SAVE_RESULTS] ERROR committing to database: {str(e)}", flush=True)
            import traceback
            print(traceback.format_exc(), flush=True)
            db.session.rollback()
            raise
        
        # Verify saved results
        try:
            saved_results = ComparisonResult.query.filter_by(comparison_id=comparison.id).count()
            print(f"[SAVE_RESULTS] Verified: {saved_results} results found in database for comparison {comparison.id}", flush=True)
            if saved_results != results_saved:
                print(f"[SAVE_RESULTS] WARNING: Mismatch! Expected {results_saved} but found {saved_results}", flush=True)
        except Exception as e:
            print(f"[SAVE_RESULTS] Error verifying saved results: {str(e)}", flush=True)
        
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


