from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from config import config
from pathlib import Path

db = SQLAlchemy()
migrate = Migrate()


def create_app(config_name='default'):
    """Application factory pattern"""
    # Get the base directory (parent of app directory)
    base_dir = Path(__file__).parent.parent.resolve()
    template_dir = base_dir / 'templates'
    static_dir = base_dir / 'app' / 'static'
    
    # Ensure directories exist
    template_dir.mkdir(exist_ok=True)
    static_dir.mkdir(parents=True, exist_ok=True)
    
    app = Flask(
        __name__,
        template_folder=str(template_dir),
        static_folder=str(static_dir),
        static_url_path='/static'
    )
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)
    
    # Check and create tables if needed
    with app.app_context():
        try:
            from app.utils.db_check import ensure_tables_exist
            ensure_tables_exist()
        except Exception as e:
            # Log error but don't fail app initialization
            import traceback
            print(f"Warning: Error ensuring tables exist: {str(e)}")
            print(traceback.format_exc())
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.connections import connections_bp
    from app.routes.projects import projects_bp
    from app.routes.comparisons import comparisons_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.tables import tables_bp
    from app.routes.users import users_bp
    from app.routes.groups import groups_bp
    from app.routes.setup import setup_bp
    from app.routes.scheduled_tasks import scheduled_tasks_bp
    from app.routes.webhooks import webhooks_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(connections_bp, url_prefix='/api/connections')
    app.register_blueprint(projects_bp, url_prefix='/api/projects')
    app.register_blueprint(comparisons_bp, url_prefix='/api/comparisons')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    app.register_blueprint(tables_bp, url_prefix='/api/tables')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(groups_bp, url_prefix='/api/groups')
    app.register_blueprint(setup_bp, url_prefix='/api/setup')
    app.register_blueprint(scheduled_tasks_bp, url_prefix='/api/scheduled-tasks')
    app.register_blueprint(webhooks_bp, url_prefix='/api/webhooks')
    
    # Register root route - redirect to login if not authenticated, otherwise redirect to home
    @app.route('/')
    def index():
        from flask import session, redirect
        user_id = session.get('user_id')
        if not user_id:
            return redirect('/login')
        # If authenticated, redirect to home page
        return redirect('/home')
    
    # Register auth template routes (login, register)
    from app.routes.auth_template import auth_template_bp
    app.register_blueprint(auth_template_bp)
    
    # Register home template route
    from app.routes.home_template import home_template_bp
    app.register_blueprint(home_template_bp)
    
    # Register template-based routes for all pages
    from app.routes.connections_template import connections_template_bp
    from app.routes.projects_template import projects_template_bp
    from app.routes.comparison_template import comparison_template_bp
    from app.routes.dashboard_template import dashboard_template_bp
    from app.routes.tables_template import tables_template_bp
    from app.routes.reports_template import reports_template_bp
    from app.routes.users_template import users_template_bp
    from app.routes.groups_template import groups_template_bp
    from app.routes.scheduled_tasks_template import scheduled_tasks_template_bp
    from app.routes.webhooks_template import webhooks_template_bp
    
    app.register_blueprint(connections_template_bp)
    app.register_blueprint(projects_template_bp)
    app.register_blueprint(comparison_template_bp)
    app.register_blueprint(dashboard_template_bp)
    app.register_blueprint(tables_template_bp)
    app.register_blueprint(reports_template_bp)
    app.register_blueprint(users_template_bp)
    app.register_blueprint(groups_template_bp)
    app.register_blueprint(scheduled_tasks_template_bp)
    app.register_blueprint(webhooks_template_bp)
    
    # Register API documentation route
    from app.routes.api_docs import api_docs_bp
    app.register_blueprint(api_docs_bp)
    
    # Initialize scheduler
    with app.app_context():
        try:
            from app.services.scheduler_service import SchedulerService
            SchedulerService.load_all_tasks()
            print("[SCHEDULER] Scheduler initialized and tasks loaded")
        except Exception as e:
            import traceback
            print(f"[SCHEDULER] Warning: Error initializing scheduler: {str(e)}")
            print(traceback.format_exc())
    
    return app

