from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from db import mysql
import os
import time
from werkzeug.utils import secure_filename

posts_bp = Blueprint('posts', __name__)

# Upload configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@posts_bp.route('/feed')
def feed():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT posts.*, users.name, users.id as user_id, users.profile_image
        FROM posts 
        JOIN users ON posts.user_id = users.id 
        ORDER BY posts.created_at DESC
    """)
    rows = cur.fetchall()
    cur.close()
    
    posts = []
    for row in rows:
        posts.append({
            'id': row[0],
            'user_id': row[1],
            'content': row[2],
            'image_url': row[3],
            'created_at': row[4],
            'name': row[5],
            'profile_image': row[7] if len(row) > 7 else None
        })
    
    # Get like counts and user likes
    from models import get_like_count, user_has_liked, get_comments_by_post
    like_counts = {}
    user_likes = {}
    post_comments = {}
    
    for post in posts:
        like_counts[post['id']] = get_like_count(post['id'])
        user_likes[post['id']] = user_has_liked(session['user_id'], post['id'])
        post_comments[post['id']] = get_comments_by_post(post['id'])
    
    # Get user stats
    from models import get_user_skills, get_user_post_count, get_follower_count
    user_skill_count = len(get_user_skills(session['user_id']))
    user_post_count = get_user_post_count(session['user_id'])
    user_connections_count = get_follower_count(session['user_id'])
    
    return render_template('feed.html', 
                           posts=posts,
                           like_counts=like_counts,
                           user_has_liked=user_likes,
                           post_comments=post_comments,
                           user_skill_count=user_skill_count,
                           user_post_count=user_post_count,
                           user_connections_count=user_connections_count)

@posts_bp.route('/comment/<int:post_id>', methods=['POST'])
def add_comment(post_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    content = request.form.get('content')
    if content:
        from models import add_comment
        add_comment(session['user_id'], post_id, content)
        flash('Comment added!', 'success')
    else:
        flash('Comment cannot be empty', 'danger')
    
    return redirect(url_for('posts.feed'))

@posts_bp.route('/delete_comment/<int:comment_id>')
def delete_comment(comment_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    from models import delete_comment
    delete_comment(comment_id, session['user_id'])
    flash('Comment deleted', 'success')
    
    return redirect(url_for('posts.feed'))

@posts_bp.route('/create', methods=['POST'])
def create_post():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    content = request.form['content']
    image_url = ''
    
    if 'image_file' in request.files:
        file = request.files['image_file']
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            name, ext = os.path.splitext(filename)
            filename = f"{name}_{session['user_id']}_{int(time.time())}{ext}"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            image_url = f'/{UPLOAD_FOLDER}/{filename}'
    else:
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
    row = cur.fetchone()
    cur.close()
    
    if not row:
        flash('Post not found', 'danger')
        return redirect(url_for('posts.feed'))
    
    post = {
        'id': row[0],
        'user_id': row[1],
        'content': row[2],
        'image_url': row[3]
    }
    
    if post['user_id'] != session['user_id']:
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
    row = cur.fetchone()
    cur.close()
    
    if not row:
        flash('Post not found', 'danger')
        return redirect(url_for('posts.feed'))
    
    if row[0] != session['user_id']:
        flash('You can only delete your own posts', 'danger')
        return redirect(url_for('posts.feed'))
    
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM posts WHERE id = %s", (post_id,))
    mysql.connection.commit()
    cur.close()
    
    flash('Post deleted successfully!', 'success')
    return redirect(url_for('posts.feed'))

@posts_bp.route('/like/<int:post_id>')
def like_post(post_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    from models import add_like
    add_like(session['user_id'], post_id)
    return redirect(url_for('posts.feed'))

@posts_bp.route('/unlike/<int:post_id>')
def unlike_post(post_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    from models import remove_like
    remove_like(session['user_id'], post_id)
    return redirect(url_for('posts.feed'))