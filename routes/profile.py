from flask import Blueprint, render_template, session, request, flash, redirect, url_for
from models import get_user_by_id, update_user_profile

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/<int:user_id>')
def view_profile(user_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    user = get_user_by_id(user_id)
    if not user:
        flash('User not found', 'danger')
        return redirect(url_for('dashboard'))
    return render_template('profile.html', user=user)

@profile_bp.route('/edit', methods=['GET', 'POST'])
def edit_profile():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        bio = request.form.get('bio')
        update_user_profile(session['user_id'], bio=bio)
        flash('Profile updated', 'success')
        return redirect(url_for('profile.view_profile', user_id=session['user_id']))
    user = get_user_by_id(session['user_id'])
    return render_template('edit_profile.html', user=user)