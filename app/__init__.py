from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.config import Config



db = SQLAlchemy()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///wallet.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    with app.app_context():
        #from . import routes
        db.create_all()  # Create sql tables for our data models

    from app.routes import wallet_bp
    app.register_blueprint(wallet_bp)

    return app




