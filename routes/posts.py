from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from db import mysql

posts_bp = Blueprint('posts', __name__)

@posts_bp.route('/feed')
def feed():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT posts.*, users.name, users.id as user_id 
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

@posts_bp.route('/edit/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM posts WHERE id = %s", (post_id,))
    post = cur.fetchone()
    cur.close()
    
    if not post:
        flash('Post not found', 'danger')
        return redirect(url_for('posts.feed'))
    
    if post[1] != session['user_id']:
        flash('You can only edit your own posts', 'danger')
        return redirect(url_for('posts.feed'))
    
    if request.method == 'POST':
        content = request.form['content']
        image_url = request.form.get('image_url', '')
        
        cur = mysql.connection.cursor()
        cur.execute("UPDATE posts SET content = %s, image_url = %s WHERE id = %s",
                    (content, image_url, post_id))
        mysql.connection.commit()
        cur.close()
        
        flash('Post updated successfully!', 'success')
        return redirect(url_for('posts.feed'))
    
    return render_template('edit_post.html', post=post)

@posts_bp.route('/delete/<int:post_id>')
def delete_post(post_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT user_id FROM posts WHERE id = %s", (post_id,))
    post = cur.fetchone()
    cur.close()
    
    if not post:
        flash('Post not found', 'danger')
        return redirect(url_for('posts.feed'))
    
    if post[0] != session['user_id']:
        flash('You can only delete your own posts', 'danger')
        return redirect(url_for('posts.feed'))
    
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM posts WHERE id = %s", (post_id,))
    mysql.connection.commit()
    cur.close()
    
    flash('Post deleted successfully!', 'success')
    return redirect(url_for('posts.feed'))
