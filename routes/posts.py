from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from db import get_db
import os
import time
from werkzeug.utils import secure_filename

posts_bp = Blueprint('posts', __name__)

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@posts_bp.route('/feed')
def feed():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT posts.*, users.name, users.id as user_id, users.profile_image
        FROM posts 
        JOIN users ON posts.user_id = users.id 
        ORDER BY posts.created_at DESC
    """)
    rows = cursor.fetchall()
    db.close()
    
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
    
    from models import get_like_count, user_has_liked, get_comments_by_post, is_following
    from models import get_user_skills, get_user_post_count, get_follower_count
    
    like_counts = {}
    user_likes = {}
    post_comments = {}
    user_following_status = {}
    
    for post in posts:
        like_counts[post['id']] = get_like_count(post['id'])
        user_likes[post['id']] = user_has_liked(session['user_id'], post['id'])
        post_comments[post['id']] = get_comments_by_post(post['id'])
        if post['user_id'] != session['user_id']:
            user_following_status[post['user_id']] = is_following(session['user_id'], post['user_id'])
    
    user_skill_count = len(get_user_skills(session['user_id']))
    user_post_count = get_user_post_count(session['user_id'])
    user_connections_count = get_follower_count(session['user_id'])
    
    return render_template('feed.html', 
                           posts=posts,
                           like_counts=like_counts,
                           user_has_liked=user_likes,
                           post_comments=post_comments,
                           user_following_status=user_following_status,
                           user_skill_count=user_skill_count,
                           user_post_count=user_post_count,
                           user_connections_count=user_connections_count)

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
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO posts (user_id, content, image_url) VALUES (?, ?, ?)",
                   (session['user_id'], content, image_url))
    db.commit()
    db.close()
    flash('Post created', 'success')
    return redirect(url_for('posts.feed'))

@posts_bp.route('/edit/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM posts WHERE id = ?", (post_id,))
    row = cursor.fetchone()
    db.close()
    
    if not row:
        flash('Post not found', 'danger')
        return redirect(url_for('posts.feed'))
    
    post = {'id': row[0], 'user_id': row[1], 'content': row[2], 'image_url': row[3]}
    
    if post['user_id'] != session['user_id']:
        flash('You can only edit your own posts', 'danger')
        return redirect(url_for('posts.feed'))
    
    if request.method == 'POST':
        content = request.form['content']
        image_url = request.form.get('image_url', '')
        
        db = get_db()
        cursor = db.cursor()
        cursor.execute("UPDATE posts SET content = ?, image_url = ? WHERE id = ?",
                       (content, image_url, post_id))
        db.commit()
        db.close()
        
        flash('Post updated successfully!', 'success')
        return redirect(url_for('posts.feed'))
    
    return render_template('edit_post.html', post=post)

@posts_bp.route('/delete/<int:post_id>')
def delete_post(post_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT user_id FROM posts WHERE id = ?", (post_id,))
    row = cursor.fetchone()
    db.close()
    
    if not row or row[0] != session['user_id']:
        flash('You can only delete your own posts', 'danger')
        return redirect(url_for('posts.feed'))
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM posts WHERE id = ?", (post_id,))
    db.commit()
    db.close()
    
    flash('Post deleted successfully!', 'success')
    return redirect(url_for('posts.feed'))

# AJAX Like/Unlike Routes
@posts_bp.route('/like/<int:post_id>', methods=['POST'])
def like_post(post_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    from models import add_like, get_like_count
    add_like(session['user_id'], post_id)
    like_count = get_like_count(post_id)
    return jsonify({'success': True, 'action': 'liked', 'like_count': like_count})

@posts_bp.route('/unlike/<int:post_id>', methods=['POST'])
def unlike_post(post_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    from models import remove_like, get_like_count
    remove_like(session['user_id'], post_id)
    like_count = get_like_count(post_id)
    return jsonify({'success': True, 'action': 'unliked', 'like_count': like_count})

# Comment Routes
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
