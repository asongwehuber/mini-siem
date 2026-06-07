from flask import Flask
from app.extensions import db, mail
from app.routes.log_routes import log_bp
from app.routes.report_routes import report_bp


def create_app():

    app = Flask(__name__)

    # DATABASE CONFIG
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        'mysql+pymysql://siemuser:StrongPassword123!@localhost/mini_siem'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # EMAIL CONFIG
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_USERNAME'] = 'minisiem09@gmail.com'
    app.config['MAIL_PASSWORD'] = 'zhnv ujqe ztrd fgod'
    app.config['MAIL_DEFAULT_SENDER'] = 'minisiem09@gmail.com'

    # INIT EXTENSIONS
    db.init_app(app)
    mail.init_app(app)

    # BLUEPRINTS
    app.register_blueprint(log_bp)
    app.register_blueprint(report_bp)

    return app