from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate

db = SQLAlchemy()
bcrypt = Bcrypt()
loginManager = LoginManager()
loginManager.login_view = 'login'
migrate = Migrate()

def createApp():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = '123'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    db.init_app(app)
    bcrypt.init_app(app)
    loginManager.init_app(app)
    migrate.init_app(app, db)
    from app.routes import router
    app.register_blueprint(router)
    with app.app_context():
        db.create_all()
    return app
