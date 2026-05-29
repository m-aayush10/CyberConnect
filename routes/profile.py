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
    
    # Fetch skills for this user
    from models import get_user_skills
    skills = get_user_skills(user_id)
    # Convert tuple to dict for easier template access
    user['skills'] = [{'id': s[0], 'skill_name': s[1], 'level': s[2]} for s in skills]
    
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

@profile_bp.route('/add_skill', methods=['POST'])
def add_skill():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    skill_name = request.form.get('skill_name')
    level = request.form.get('level', 'Beginner')
    if skill_name:
        from models import add_skill
        add_skill(session['user_id'], skill_name, level)
        flash('Skill added!', 'success')
    else:
        flash('Skill name required', 'danger')
    return redirect(url_for('profile.view_profile', user_id=session['user_id']))

@profile_bp.route('/delete_skill/<int:skill_id>')
def delete_skill(skill_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    from models import delete_skill
    delete_skill(skill_id, session['user_id'])
    flash('Skill removed', 'success')
    return redirect(url_for('profile.view_profile', user_id=session['user_id']))
