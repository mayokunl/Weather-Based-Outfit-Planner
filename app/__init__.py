from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import config
import markdown
import re

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    
    # Add custom template filters
    @app.template_filter('markdown')
    def markdown_filter(text):
        """Convert markdown to HTML, with basic formatting support."""
        if not text:
            return text
        
        # Simple markdown-like replacements
        # Convert **text** to <strong>text</strong>
        text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
        
        # Convert *text* to <em>text</em>
        text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
        
        # Convert newlines to <br> tags
        text = text.replace('\n', '<br>')
        
        return text
    
    # Import models to ensure they're registered with SQLAlchemy
    from app.models import user, closet
    from app.models.trip import Trip
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.recommendations import recommendations_bp
    from app.routes.closet import closet_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(recommendations_bp)
    app.register_blueprint(closet_bp)
    
    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return db.session.get(User, int(user_id))
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app
