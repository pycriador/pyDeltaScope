from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timedelta
from croniter import croniter
import requests
import os
from app.models.scheduled_task import ScheduledTask
from app.models.comparison import Comparison, ComparisonResult
from app.models.project import Project
from app import db
from app.services.comparison_service import ComparisonService
from app.services.database import DatabaseService


class SchedulerService:
    """Service for managing scheduled tasks"""
    
    _scheduler = None
    _running_tasks = set()  # Track currently running tasks to prevent duplicates
    
    @classmethod
    def get_scheduler(cls):
        """Get or create scheduler instance"""
        if cls._scheduler is None:
            cls._scheduler = BackgroundScheduler()
            cls._scheduler.start()
            print(f"[SCHEDULER] Created new scheduler instance", flush=True)
        elif not cls._scheduler.running:
            print(f"[SCHEDULER] Scheduler was stopped, restarting...", flush=True)
            cls._scheduler.start()
        return cls._scheduler
    
    @classmethod
    def calculate_next_run(cls, schedule_type, schedule_value, last_run=None):
        """Calculate next run time based on schedule type and value"""
        now = datetime.utcnow()
        
        if schedule_type == 'preset':
            if schedule_value == '15min':
                return now + timedelta(minutes=15)
            elif schedule_value == '1hour':
                return now + timedelta(hours=1)
            elif schedule_value == '6hours':
                return now + timedelta(hours=6)
            elif schedule_value == '12hours':
                return now + timedelta(hours=12)
            elif schedule_value == 'daily':
                # Next day at midnight UTC
                next_day = now + timedelta(days=1)
                return next_day.replace(hour=0, minute=0, second=0, microsecond=0)
        
        elif schedule_type == 'interval':
            # schedule_value is minutes
            minutes = int(schedule_value)
            return now + timedelta(minutes=minutes)
        
        elif schedule_type == 'cron':
            # schedule_value is cron expression
            try:
                cron = croniter(schedule_value, now)
                return cron.get_next(datetime)
            except Exception as e:
                raise ValueError(f"Invalid cron expression: {str(e)}")
        
        return now
    
    @classmethod
    def get_trigger(cls, schedule_type, schedule_value):
        """Get APScheduler trigger based on schedule type"""
        if schedule_type == 'preset':
            if schedule_value == '15min':
                return IntervalTrigger(minutes=15)
            elif schedule_value == '1hour':
                return IntervalTrigger(hours=1)
            elif schedule_value == '6hours':
                return IntervalTrigger(hours=6)
            elif schedule_value == '12hours':
                return IntervalTrigger(hours=12)
            elif schedule_value == 'daily':
                return CronTrigger(hour=0, minute=0)  # Daily at midnight
        
        elif schedule_type == 'interval':
            minutes = int(schedule_value)
            return IntervalTrigger(minutes=minutes)
        
        elif schedule_type == 'cron':
            # Parse cron expression: "minute hour day month day_of_week"
            parts = schedule_value.split()
            if len(parts) == 5:
                return CronTrigger(
                    minute=parts[0],
                    hour=parts[1],
                    day=parts[2],
                    month=parts[3],
                    day_of_week=parts[4]
                )
            else:
                raise ValueError(f"Invalid cron expression format: {schedule_value}")
        
        raise ValueError(f"Unknown schedule type: {schedule_type}")
    
    @classmethod
    def execute_scheduled_task(cls, task_id):
        """Execute a scheduled task"""
        # Prevent duplicate executions
        if task_id in cls._running_tasks:
            print(f"[SCHEDULER] Task {task_id} is already running, skipping duplicate execution", flush=True)
            return
        
        # Mark task as running
        cls._running_tasks.add(task_id)
        
        try:
            from flask import Flask
            from app import create_app
            
            # Get or create app instance for background execution
            app = None
            try:
                from flask import current_app
                app = current_app._get_current_object()
            except RuntimeError:
                # No application context, create one
                app = create_app()
            
            with app.app_context():
                try:
                    task = ScheduledTask.query.get(task_id)
                    if not task or not task.is_active:
                        print(f"[SCHEDULER] Task {task_id} not found or inactive", flush=True)
                        return
                    
                    # Update task status
                    task.last_run_at = datetime.utcnow()
                    task.last_run_status = 'running'
                    task.total_runs += 1
                    db.session.commit()
                    
                    print(f"[SCHEDULER] Executing task {task_id}: {task.name}", flush=True)
                    
                    # Get project
                    project = Project.query.get(task.project_id)
                    if not project:
                        raise Exception(f"Project {task.project_id} not found")
                    
                    print(f"[SCHEDULER] ========== TASK EXECUTION START ==========", flush=True)
                    print(f"[SCHEDULER] Task ID: {task_id}, Name: {task.name}", flush=True)
                    print(f"[SCHEDULER] Task key_mappings from DB (raw): {task.key_mappings}", flush=True)
                    print(f"[SCHEDULER] Task key_mappings type (raw): {type(task.key_mappings)}", flush=True)
                    if task.key_mappings:
                        print(f"[SCHEDULER] Task key_mappings items (raw): {list(task.key_mappings.items()) if isinstance(task.key_mappings, dict) else 'NOT A DICT'}", flush=True)
                    
                    # Get connection configs
                    source_config = project.source_connection.get_decrypted_config()
                    source_config['type'] = project.source_connection.db_type
                    
                    target_config = project.target_connection.get_decrypted_config()
                    target_config['type'] = project.target_connection.db_type
                    
                    # Get primary keys
                    source_engine = DatabaseService.get_engine(source_config, already_decrypted=True)
                    primary_keys = DatabaseService.get_primary_keys(source_engine, project.source_table)
                    print(f"[SCHEDULER] Primary keys found from DB: {primary_keys}", flush=True)
                    
                    # If no primary keys found, try to infer from table data
                    if not primary_keys:
                        print(f"[SCHEDULER] No PK found in DB, trying to infer from table structure...", flush=True)
                        # Get table data to check for common PK names
                        source_df_temp = DatabaseService.get_table_data(source_engine, project.source_table)
                        common_pk_names = ['id', 'ID', 'Id', '_id', 'pk_id', 'primary_key']
                        for pk_name in common_pk_names:
                            if pk_name in source_df_temp.columns:
                                primary_keys = [pk_name]
                                print(f"[SCHEDULER] Found common PK name '{pk_name}' in table columns", flush=True)
                                break
                        
                        if not primary_keys:
                            print(f"[SCHEDULER] WARNING: No PK found! Will use all columns as PK (this may cause issues)", flush=True)
                    
                    print(f"[SCHEDULER] Final primary keys to use: {primary_keys}", flush=True)
                    
                    # Use key mappings from task
                    key_mappings = task.key_mappings or {}
                    
                    # Ensure key_mappings is a dict (JSON might return None or other types)
                    if key_mappings is None:
                        key_mappings = {}
                    elif not isinstance(key_mappings, dict):
                        print(f"[SCHEDULER] WARNING: key_mappings is not a dict, converting. Type: {type(key_mappings)}, Value: {key_mappings}", flush=True)
                        try:
                            if isinstance(key_mappings, str):
                                import json
                                key_mappings = json.loads(key_mappings)
                            else:
                                key_mappings = {}
                        except:
                            key_mappings = {}
                    
                    print(f"[SCHEDULER] Key mappings (after validation): {key_mappings}", flush=True)
                    print(f"[SCHEDULER] Key mappings type: {type(key_mappings)}, empty: {not key_mappings}, length: {len(key_mappings) if isinstance(key_mappings, dict) else 0}", flush=True)
                    if key_mappings:
                        print(f"[SCHEDULER] Key mappings content: {list(key_mappings.items())}", flush=True)
                    else:
                        print(f"[SCHEDULER] WARNING: Key mappings are EMPTY! This might be the problem!", flush=True)
                    print(f"[SCHEDULER] Source table: {project.source_table}, Target table: {project.target_table}", flush=True)
                    print(f"[SCHEDULER] Primary keys: {primary_keys}", flush=True)
                    
                    # Run comparison
                    print(f"[SCHEDULER] ========== CALLING COMPARISON SERVICE ==========", flush=True)
                    print(f"[SCHEDULER] Starting comparison with key_mappings={key_mappings}...", flush=True)
                    differences_df, differences = ComparisonService.compare_tables(
                        source_config,
                        target_config,
                        project.source_table,
                        project.target_table,
                        primary_keys,
                        key_mappings
                    )
                    
                    print(f"[SCHEDULER] Comparison function returned {len(differences)} differences", flush=True)
                    print(f"[SCHEDULER] Differences type: {type(differences)}, is list: {isinstance(differences, list)}", flush=True)
                    print(f"[SCHEDULER] Comparison completed. DataFrame shape: {differences_df.shape if not differences_df.empty else 'empty'}, Differences count: {len(differences)}", flush=True)
                    
                    # Debug: Print first few differences
                    if len(differences) > 0:
                        print(f"[SCHEDULER] First difference sample: {differences[0] if differences else 'None'}", flush=True)
                    else:
                        print(f"[SCHEDULER] INFO: No differences found between source table '{project.source_table}' and target table '{project.target_table}'", flush=True)
                        print(f"[SCHEDULER] This could mean: tables are identical, key mappings are incorrect, or tables are empty", flush=True)
                    
                    # Save results
                    print(f"[SCHEDULER] Saving results to database...", flush=True)
                    comparison = ComparisonService.save_comparison_results(
                        task.project_id,
                        differences,
                        metadata={
                            'primary_keys': primary_keys,
                            'key_mappings': key_mappings,
                            'total_source_rows': len(differences_df) if not differences_df.empty else 0,
                            'scheduled_task_id': task_id
                        },
                        user_id=task.user_id
                    )
                    
                    print(f"[SCHEDULER] Task {task_id} completed successfully. Found {len(differences)} differences. Comparison ID: {comparison.id}", flush=True)
                    
                    # Force flush and commit to ensure data is persisted
                    db.session.flush()
                    db.session.commit()
                    
                    # Verify results were saved (use a fresh query)
                    db.session.expire_all()  # Refresh all objects from database
                    saved_count = ComparisonResult.query.filter_by(comparison_id=comparison.id).count()
                    print(f"[SCHEDULER] Verification: {saved_count} results saved in database for comparison {comparison.id}", flush=True)
                    
                    if saved_count == 0 and len(differences) > 0:
                        print(f"[SCHEDULER] ERROR: Results were not saved! Expected {len(differences)} but found {saved_count}", flush=True)
                        # Try to save again
                        print(f"[SCHEDULER] Attempting to re-save results...", flush=True)
                        db.session.refresh(comparison)
                        for diff in differences[:5]:  # Try first 5
                            try:
                                result = ComparisonResult(
                                    comparison_id=comparison.id,
                                    record_id=str(diff.get('record_id')) if diff.get('record_id') is not None else None,
                                    field_name=diff.get('field_name'),
                                    source_value=str(diff.get('source_value')) if diff.get('source_value') is not None else None,
                                    target_value=str(diff.get('target_value')) if diff.get('target_value') is not None else None,
                                    change_type=diff.get('change_type')
                                )
                                db.session.add(result)
                            except Exception as e:
                                print(f"[SCHEDULER] Error re-saving diff: {str(e)}", flush=True)
                        db.session.commit()
                        saved_count_retry = ComparisonResult.query.filter_by(comparison_id=comparison.id).count()
                        print(f"[SCHEDULER] After retry: {saved_count_retry} results found", flush=True)
                    
                    # Update task status
                    task = ScheduledTask.query.get(task_id)
                    if task:
                        task.last_run_status = 'success'
                        task.last_run_message = f'Comparison completed successfully. Found {len(differences)} differences.'
                        task.successful_runs += 1
                        task.next_run_at = cls.calculate_next_run(
                            task.schedule_type,
                            task.schedule_value,
                            task.last_run_at
                        )
                        db.session.commit()
            
                except Exception as e:
                    import traceback
                    error_msg = str(e)
                    print(f"[SCHEDULER] Error executing task {task_id}: {error_msg}", flush=True)
                    print(traceback.format_exc(), flush=True)
                    
                    # Update task status with error
                    try:
                        task = ScheduledTask.query.get(task_id)
                        if task:
                            task.last_run_status = 'failed'
                            task.last_run_message = error_msg[:500]  # Limit message length
                            task.failed_runs += 1
                            task.next_run_at = cls.calculate_next_run(
                                task.schedule_type,
                                task.schedule_value,
                                task.last_run_at
                            )
                            db.session.commit()
                    except Exception as db_error:
                        print(f"[SCHEDULER] Error updating task status: {str(db_error)}", flush=True)
                        import traceback
                        print(traceback.format_exc(), flush=True)
                        db.session.rollback()
        finally:
            # Remove task from running set
            cls._running_tasks.discard(task_id)
            print(f"[SCHEDULER] Task {task_id} execution completed, removed from running set", flush=True)
    
    @classmethod
    def load_all_tasks(cls):
        """Load all active scheduled tasks into scheduler"""
        from flask import Flask
        from app import create_app
        
        # Get or create app instance
        app = None
        try:
            from flask import current_app
            app = current_app._get_current_object()
        except RuntimeError:
            app = create_app()
        
        with app.app_context():
            scheduler = cls.get_scheduler()
            
            # Remove all existing jobs
            scheduler.remove_all_jobs()
            print("[SCHEDULER] Removed all existing jobs")
            
            # Load active tasks
            tasks = ScheduledTask.query.filter_by(is_active=True).all()
            print(f"[SCHEDULER] Found {len(tasks)} active tasks to load")
            
            for task in tasks:
                try:
                    job_id = f'scheduled_task_{task.id}'
                    
                    # Check for existing jobs with same ID
                    existing_jobs = [j for j in scheduler.get_jobs() if j.id == job_id]
                    if existing_jobs:
                        print(f"[SCHEDULER] Found {len(existing_jobs)} existing job(s) with ID {job_id}, removing before adding", flush=True)
                        for existing_job in existing_jobs:
                            try:
                                scheduler.remove_job(existing_job.id)
                            except:
                                pass
                    
                    trigger = cls.get_trigger(task.schedule_type, task.schedule_value)
                    scheduler.add_job(
                        cls.execute_scheduled_task,
                        trigger=trigger,
                        args=[task.id],
                        id=job_id,
                        replace_existing=True
                    )
                    
                    # Verify only one job was added
                    jobs_after = [j for j in scheduler.get_jobs() if j.id == job_id]
                    if len(jobs_after) > 1:
                        print(f"[SCHEDULER] WARNING: Multiple jobs with ID {job_id} found after add!", flush=True)
                        # Keep only the first one
                        for dup_job in jobs_after[1:]:
                            try:
                                scheduler.remove_job(dup_job.id)
                            except:
                                pass
                    
                    print(f"[SCHEDULER] Loaded task: {task.name} (ID: {task.id}, Type: {task.schedule_type}, Value: {task.schedule_value})", flush=True)
                except Exception as e:
                    import traceback
                    print(f"[SCHEDULER] Error loading task {task.id}: {str(e)}", flush=True)
                    print(traceback.format_exc(), flush=True)
            
            # Print scheduler status
            jobs = scheduler.get_jobs()
            print(f"[SCHEDULER] Scheduler is running with {len(jobs)} jobs")
            for job in jobs:
                print(f"[SCHEDULER]   - Job ID: {job.id}, Next run: {job.next_run_time}")
    
    @classmethod
    def add_task(cls, task_id):
        """Add a single task to scheduler"""
        from flask import Flask
        from app import create_app
        
        # Get or create app instance
        app = None
        try:
            from flask import current_app
            app = current_app._get_current_object()
        except RuntimeError:
            app = create_app()
        
        with app.app_context():
            scheduler = cls.get_scheduler()
            task = ScheduledTask.query.get(task_id)
            
            if not task or not task.is_active:
                print(f"[SCHEDULER] Task {task_id} not found or inactive, skipping")
                return
            
            try:
                job_id = f'scheduled_task_{task.id}'
                
                # Check if job already exists
                existing_job = scheduler.get_job(job_id)
                if existing_job:
                    print(f"[SCHEDULER] Job {job_id} already exists, removing before adding new one", flush=True)
                    scheduler.remove_job(job_id)
                
                # Remove existing job if it exists to avoid duplicates
                try:
                    scheduler.remove_job(job_id)
                    print(f"[SCHEDULER] Removed existing job {job_id} before adding new one", flush=True)
                except:
                    pass  # Job doesn't exist, that's fine
                
                # Verify no duplicate jobs exist
                all_jobs = scheduler.get_jobs()
                duplicate_jobs = [j for j in all_jobs if j.id == job_id]
                if duplicate_jobs:
                    print(f"[SCHEDULER] WARNING: Found {len(duplicate_jobs)} duplicate jobs with ID {job_id}, removing all", flush=True)
                    for dup_job in duplicate_jobs:
                        try:
                            scheduler.remove_job(dup_job.id)
                        except:
                            pass
                
                trigger = cls.get_trigger(task.schedule_type, task.schedule_value)
                scheduler.add_job(
                    cls.execute_scheduled_task,
                    trigger=trigger,
                    args=[task.id],
                    id=job_id,
                    replace_existing=True
                )
                
                # Verify job was added correctly
                job = scheduler.get_job(job_id)
                all_jobs_after = scheduler.get_jobs()
                jobs_with_same_id = [j for j in all_jobs_after if j.id == job_id]
                
                if len(jobs_with_same_id) > 1:
                    print(f"[SCHEDULER] ERROR: Found {len(jobs_with_same_id)} jobs with same ID {job_id}!", flush=True)
                    # Remove duplicates, keep only the first one
                    for dup_job in jobs_with_same_id[1:]:
                        try:
                            scheduler.remove_job(dup_job.id)
                            print(f"[SCHEDULER] Removed duplicate job: {dup_job.id}", flush=True)
                        except:
                            pass
                
                print(f"[SCHEDULER] Added task: {task.name} (ID: {task.id}, Type: {task.schedule_type}, Value: {task.schedule_value})", flush=True)
                if job:
                    print(f"[SCHEDULER]   Next run: {job.next_run_time}", flush=True)
                print(f"[SCHEDULER]   Total jobs in scheduler: {len(scheduler.get_jobs())}", flush=True)
            except Exception as e:
                import traceback
                print(f"[SCHEDULER] Error adding task {task.id}: {str(e)}")
                print(traceback.format_exc())
    
    @classmethod
    def remove_task(cls, task_id):
        """Remove a task from scheduler"""
        scheduler = cls.get_scheduler()
        try:
            scheduler.remove_job(f'scheduled_task_{task_id}')
            print(f"[SCHEDULER] Removed task ID: {task_id}")
        except Exception as e:
            print(f"[SCHEDULER] Error removing task {task_id}: {str(e)}")

