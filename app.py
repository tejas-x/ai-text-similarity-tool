from flask import Flask
from flask_login import LoginManager
from config import Config
from models.db import init_db, get_user_by_id
from routes.auth import auth_bp
from routes.main import main_bp
from routes.analysis import analysis_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # DB
    init_db(app)

    # Login
    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return get_user_by_id(user_id)

    # Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(analysis_bp)

    # Jinja globals
    @app.context_processor
    def inject_roles():
        return dict(ROLES=["student", "faculty"])

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)