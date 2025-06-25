import redis
from flask import Flask, request, redirect, url_for, flash, render_template
from dotenv import load_dotenv

import os

from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin

load_dotenv()

app = Flask(__name__)

login_manager = LoginManager()
login_manager.init_app(app)

app.secret_key = os.getenv('SECRET_KEY')
BASE_API_URL = os.getenv('BASE_API_URL')


redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
redis_conn = redis.Redis.from_url(redis_url, decode_responses=True)
CACHE_EXPIRE_SECONDS = int(os.getenv('CACHE_EXPIRE_SECONDS', 3600))

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")


from app.routes import main, reactions, admin

app.register_blueprint(main.bp)
app.register_blueprint(reactions.bp)
app.register_blueprint(admin.admin_bp)


class User(UserMixin):
    def __init__(self, id):
        self.id = id


@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            user = User(1)
            login_user(user)
            return redirect(url_for('admin.admin_dashboard'))
        else:
            flash('Неверное имя пользователя или пароль', 'danger')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))