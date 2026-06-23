from flask import Flask
from app.extensions import db, mail
from app.routes.log_routes import log_bp
from app.routes.report_routes import report_bp
from app.routes.ai import ai_bp
from app.routes.chat import chat_bp
import os
from dotenv import load_dotenv


load_dotenv()


def create_app():

    app = Flask(__name__)
    

    # DATABASE CONFIG
    # DATABASE CONFIG
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"mysql+pymysql://"
        f"{os.getenv('DB_USER')}:"
        f"{os.getenv('DB_PASSWORD')}@"
        f"{os.getenv('DB_HOST')}/"
        f"{os.getenv('DB_NAME')}"
    )

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # EMAIL CONFIG
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

    # INIT EXTENSIONS
    db.init_app(app)
    mail.init_app(app)

    # BLUEPRINTS
    app.register_blueprint(log_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(ai_bp, url_prefix="/ai")

    return app