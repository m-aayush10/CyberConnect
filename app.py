import os
from flask import Flask, render_template, request, redirect, url_for, session
import dotenv
from flask_mysqldb import MySQL

dotenv.load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')

mysql = MySQL(app)

from routes.auth import auth_bp
from routes.profile import profile_bp
from routes.posts import posts_bp
from routes.connections import connections_bp
from routes.admin import admin_bp


app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(profile_bp, url_prefix='/profile')
app.register_blueprint(posts_bp, url_prefix='/posts')
app.register_blueprint(connections_bp, url_prefix='/connections')
app.register_blueprint(admin_bp, url_prefix='/admin')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(debug=True)


