from flask import Flask
# from flask_sqlalchemy import SQLAlchemy

def create_app():
    app = Flask(__name__)

    from .routes.main import main_bp
    from .routes.api import api_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    return app