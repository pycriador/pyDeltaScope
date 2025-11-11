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
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(connections_bp, url_prefix='/api/connections')
    app.register_blueprint(projects_bp, url_prefix='/api/projects')
    app.register_blueprint(comparisons_bp, url_prefix='/api/comparisons')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    app.register_blueprint(tables_bp, url_prefix='/api/tables')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(groups_bp, url_prefix='/api/groups')
    app.register_blueprint(setup_bp, url_prefix='/api/setup')
    
    # Register root route and SPA routes
    @app.route('/')
    @app.route('/conexoes')
    @app.route('/projetos')
    @app.route('/comparacao')
    @app.route('/dashboard')
    @app.route('/tabelas')
    @app.route('/relatorios')
    @app.route('/usuarios')
    @app.route('/grupos')
    def index():
        from flask import render_template
        return render_template('index.html')
    
    # Register API documentation route
    from app.routes.api_docs import api_docs_bp
    app.register_blueprint(api_docs_bp)
    
    return app

