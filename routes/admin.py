from flask import Blueprint, render_template, session, flash, redirect, url_for
from functools import wraps

admin_bp = Blueprint('admin', __name__)

# ── Admin decorator ──
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_role') == 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# ── Admin dashboard ──
@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    from models import get_all_users, get_all_posts
    users = get_all_users()
    posts = get_all_posts()
    return render_template('admin.html', users=users, posts=posts)

# ── Delete a user (admin only) ──
@admin_bp.route('/delete_user/<int:user_id>')
@admin_required
def delete_user(user_id):
    from models import delete_user
    delete_user(user_id)
    flash('User deleted.', 'success')
    return redirect(url_for('admin.dashboard'))

# ── Delete a post (admin override) ──
@admin_bp.route('/delete_post/<int:post_id>')
@admin_required
def delete_post(post_id):
    from models import delete_post_by_admin
    delete_post_by_admin(post_id)
    flash('Post deleted.', 'success')
    return redirect(url_for('admin.dashboard'))