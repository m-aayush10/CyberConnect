from flask import Blueprint, render_template, session, redirect, url_for, flash, jsonify
from models import get_notifications, get_unread_count, mark_notification_read, mark_all_notifications_read

notifications_bp = Blueprint('notifications', __name__)

@notifications_bp.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    notifications = get_notifications(session['user_id'], limit=50)
    unread_count = get_unread_count(session['user_id'])
    
    return render_template('notifications.html', 
                         notifications=notifications,
                         unread_count=unread_count)

@notifications_bp.route('/unread_count')
def unread_count():
    if 'user_id' not in session:
        return jsonify({'count': 0})
    
    count = get_unread_count(session['user_id'])
    return jsonify({'count': count})

@notifications_bp.route('/mark_read/<int:notification_id>')
def mark_read(notification_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    mark_notification_read(notification_id, session['user_id'])
    return redirect(url_for('notifications.index'))

@notifications_bp.route('/mark_all_read')
def mark_all_read():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    mark_all_notifications_read(session['user_id'])
    flash('All notifications marked as read', 'success')
    return redirect(url_for('notifications.index'))
