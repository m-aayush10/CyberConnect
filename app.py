import os
from flask import Flask, render_template, request, redirect, url_for, session
import dotenv
from db import mysql

dotenv.load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', 'Messi@123')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB', 'cyberconnect')

mysql.init_app(app)

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
    
    from models import get_user_skills, get_user_post_count, get_follower_count
    
    user_id = session['user_id']
    skills = get_user_skills(user_id)
    skill_count = len(skills) if skills else 0
    post_count = get_user_post_count(user_id)
    connections_count = get_follower_count(user_id)
    
    return render_template('dashboard.html', 
                         user_skill_count=skill_count,
                         user_post_count=post_count,
                         user_connections_count=connections_count)

if __name__ == '__main__':
    app.run(debug=True)