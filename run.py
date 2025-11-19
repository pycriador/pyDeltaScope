import os
from app import create_app, db
from app.models import User, Project, Comparison, ComparisonResult, ChangeLog, DatabaseConnection

app = create_app(os.getenv('FLASK_ENV', 'default'))


@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Project': Project,
        'Comparison': Comparison,
        'ComparisonResult': ComparisonResult,
        'ChangeLog': ChangeLog,
        'DatabaseConnection': DatabaseConnection
    }


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    # Allow port to be set via environment variable (for start.py script)
    port = int(os.environ.get('FLASK_RUN_PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)


