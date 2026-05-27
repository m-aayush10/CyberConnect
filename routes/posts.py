from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from db import mysql

posts_bp = Blueprint('posts', __name__)

@posts_bp.route('/feed')
def feed():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT posts.*, users.name 
        FROM posts 
        JOIN users ON posts.user_id = users.id 
        ORDER BY posts.created_at DESC
    """)
    posts = cur.fetchall()
    cur.close()
    return render_template('feed.html', posts=posts)

@posts_bp.route('/create', methods=['POST'])
def create_post():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    content = request.form['content']
    image_url = request.form.get('image_url', '')
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO posts (user_id, content, image_url) VALUES (%s, %s, %s)",
                (session['user_id'], content, image_url))
    mysql.connection.commit()
    cur.close()
    flash('Post created', 'success')
    return redirect(url_for('posts.feed'))
