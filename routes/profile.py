from flask import Blueprint, render_template, session, request, flash, redirect, url_for, jsonify
from models import get_user_by_id, update_user_profile
import os
import time
from werkzeug.utils import secure_filename

profile_bp = Blueprint('profile', __name__)

UPLOAD_FOLDER = 'static/profile_pics'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# SEARCH USERS
@profile_bp.route('/search')
def search_users():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    query = request.args.get('q', '').strip()
    results = []
    suggestions = []
    
    if query:
        from models import search_users, is_following
        raw_results = search_users(query, session['user_id'])
        for user in raw_results:
            user['following'] = is_following(session['user_id'], user['id'])
            results.append(user)
        
        # If no results, get suggestions
        if not results:
            from models import get_suggested_users
            raw_suggestions = get_suggested_users(session['user_id'], 5)
            for user in raw_suggestions:
                user['following'] = False  # They are not following these users
                suggestions.append(user)
    
    return render_template('search_results.html', 
                         query=query, 
                         results=results, 
                         suggestions=suggestions)

# VIEW PROFILE
@profile_bp.route('/<int:user_id>')
def view_profile(user_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    user = get_user_by_id(user_id)
    if not user:
        flash('User not found', 'danger')
        return redirect(url_for('dashboard'))
    
    from models import get_user_skills, get_user_certifications, get_follower_count
    from models import get_following_count, is_following, get_followers, get_following, get_user_posts
    
    user['skills'] = get_user_skills(user_id)
    user['certifications'] = get_user_certifications(user_id)
    follower_count = get_follower_count(user_id)
    following_count = get_following_count(user_id)
    following_status = is_following(session['user_id'], user_id) if session['user_id'] != user_id else False
    followers_list = get_followers(user_id)
    following_list = get_following(user_id)
    cover_photo = user.get('cover_photo')
    user_posts = get_user_posts(user_id)
    
    return render_template('profile.html', user=user, 
                           follower_count=follower_count,
                           following_count=following_count,
                           is_following=following_status,
                           followers=followers_list,
                           following=following_list,
                           cover_photo=cover_photo,
                           user_posts=user_posts,
                           posts_count=len(user_posts))

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

@profile_bp.route('/edit_skill/<int:skill_id>', methods=['GET', 'POST'])
def edit_skill(skill_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    from models import get_skill_by_id, update_skill
    
    skill = get_skill_by_id(skill_id)
    if not skill:
        flash('Skill not found', 'danger')
        return redirect(url_for('profile.view_profile', user_id=session['user_id']))
    
    if skill['user_id'] != session['user_id']:
        flash('You can only edit your own skills', 'danger')
        return redirect(url_for('profile.view_profile', user_id=session['user_id']))
    
    if request.method == 'POST':
        skill_name = request.form.get('skill_name')
        level = request.form.get('level')
        if skill_name:
            update_skill(skill_id, skill_name, level)
            flash('Skill updated!', 'success')
        else:
            flash('Skill name is required', 'danger')
        return redirect(url_for('profile.view_profile', user_id=session['user_id']))
    
    return render_template('edit_skill.html', skill=skill)

@profile_bp.route('/add_certification', methods=['POST'])
def add_certification():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    title = request.form.get('title')
    issuer = request.form.get('issuer')
    date_earned = request.form.get('date_earned') or None
    credential_url = request.form.get('credential_url') or None
    
    if title and issuer:
        from models import add_certification
        add_certification(session['user_id'], title, issuer, date_earned, credential_url)
        flash('Certification added!', 'success')
    else:
        flash('Title and issuer are required', 'danger')
    return redirect(url_for('profile.view_profile', user_id=session['user_id']))

@profile_bp.route('/edit_certification/<int:cert_id>', methods=['GET', 'POST'])
def edit_certification(cert_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    from models import get_certification_by_id, update_certification
    
    cert = get_certification_by_id(cert_id)
    if not cert:
        flash('Certification not found', 'danger')
        return redirect(url_for('profile.view_profile', user_id=session['user_id']))
    
    if cert['user_id'] != session['user_id']:
        flash('You can only edit your own certifications', 'danger')
        return redirect(url_for('profile.view_profile', user_id=session['user_id']))
    
    if request.method == 'POST':
        title = request.form.get('title')
        issuer = request.form.get('issuer')
        date_earned = request.form.get('date_earned') or None
        credential_url = request.form.get('credential_url') or None
        
        if title and issuer:
            update_certification(cert_id, title, issuer, date_earned, credential_url)
            flash('Certification updated!', 'success')
        else:
            flash('Title and issuer are required', 'danger')
        return redirect(url_for('profile.view_profile', user_id=session['user_id']))
    
    return render_template('edit_certification.html', cert=cert)

@profile_bp.route('/delete_certification/<int:cert_id>')
def delete_certification(cert_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    from models import delete_certification
    delete_certification(cert_id, session['user_id'])
    flash('Certification removed', 'success')
    return redirect(url_for('profile.view_profile', user_id=session['user_id']))

@profile_bp.route('/upload_picture', methods=['POST'])
def upload_picture():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if 'profile_pic' not in request.files:
        flash('No file selected', 'danger')
        return redirect(url_for('profile.edit_profile'))
    
    file = request.files['profile_pic']
    if file.filename == '':
        flash('No file selected', 'danger')
        return redirect(url_for('profile.edit_profile'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        name, ext = os.path.splitext(filename)
        filename = f"user_{session['user_id']}_{int(time.time())}{ext}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        from models import update_profile_picture
        update_profile_picture(session['user_id'], f'/{UPLOAD_FOLDER}/{filename}')
        session['user_profile_image'] = f'/{UPLOAD_FOLDER}/{filename}'
        
        flash('Profile picture updated!', 'success')
    else:
        flash('Invalid file type. Use PNG, JPG, JPEG, GIF, or WEBP', 'danger')
    
    return redirect(url_for('profile.edit_profile'))

@profile_bp.route('/upload_cover', methods=['POST'])
def upload_cover():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if 'cover_photo' not in request.files:
        flash('No file selected', 'danger')
        return redirect(url_for('profile.edit_profile'))
    
    file = request.files['cover_photo']
    if file.filename == '':
        flash('No file selected', 'danger')
        return redirect(url_for('profile.edit_profile'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        name, ext = os.path.splitext(filename)
        filename = f"cover_{session['user_id']}_{int(time.time())}{ext}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        from models import update_cover_photo
        update_cover_photo(session['user_id'], f'/{UPLOAD_FOLDER}/{filename}')
        
        flash('Cover photo updated!', 'success')
    else:
        flash('Invalid file type. Use PNG, JPG, JPEG, GIF, or WEBP', 'danger')
    
    return redirect(url_for('profile.edit_profile'))

# AJAX Follow/Unfollow Routes
@profile_bp.route('/follow/<int:user_id>', methods=['GET', 'POST'])
def follow(user_id):
    if 'user_id' not in session:
        if request.method == 'GET':
            return redirect(url_for('auth.login'))
        return jsonify({'error': 'Not logged in'}), 401
    
    if session['user_id'] == user_id:
        if request.method == 'GET':
            flash('You cannot follow yourself', 'danger')
            return redirect(request.referrer or url_for('profile.search_users'))
        return jsonify({'error': 'Cannot follow yourself'}), 400
    
    from models import follow_user
    success = follow_user(session['user_id'], user_id)
    
    if request.method == 'GET':
        if success:
            flash('User followed!', 'success')
        else:
            flash('Already following', 'danger')
        return redirect(request.referrer or url_for('profile.search_users'))
    
    # POST (AJAX) response
    if success:
        return jsonify({'success': True, 'action': 'followed'})
    else:
        return jsonify({'error': 'Already following'}), 400

@profile_bp.route('/unfollow/<int:user_id>', methods=['GET', 'POST'])
def unfollow(user_id):
    if 'user_id' not in session:
        if request.method == 'GET':
            return redirect(url_for('auth.login'))
        return jsonify({'error': 'Not logged in'}), 401
    
    from models import unfollow_user
    unfollow_user(session['user_id'], user_id)
    
    if request.method == 'GET':
        flash('User unfollowed', 'success')
        return redirect(request.referrer or url_for('profile.search_users'))
    
    return jsonify({'success': True, 'action': 'unfollowed'})

# SELF-DELETE ACCOUNT (Complete User CRUD)
@profile_bp.route('/delete_account', methods=['POST'])
def delete_account():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    from models import delete_user_by_id
    
    user_id = session['user_id']
    delete_user_by_id(user_id)
    
    session.clear()
    flash('Your account has been deleted.', 'info')
    return redirect(url_for('index'))