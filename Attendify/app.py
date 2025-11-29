from flask import Flask
from config import Config
from models import db, User
from routes import bp
from flask_login import LoginManager
from utils import hash_password
import os

def create_app():
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(Config)
    os.makedirs(os.path.join(app.root_path, 'instance'), exist_ok=True)

    db.init_app(app)

    login = LoginManager()
    login.login_view = 'main.login'
    login.init_app(app)

    @login.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    app.register_blueprint(bp)

    with app.app_context():
        db.create_all()
        # create an admin user if none exists
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', password_hash=hash_password('admin123'), role='admin')
            db.session.add(admin)
            db.session.commit()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
