from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import bcrypt
from models import get_user_by_email, create_user

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # If user is already logged in, redirect to dashboard
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = get_user_by_email(email)


        print("\n========== LOGIN DEBUG ==========")
        print("Email:", email)
        print("User from DB:", user)

        if user:
            print("User ID:", user.get("id"))
            print("Profile Image:", user.get("profile_image"))
        else:
            print("User not found")

        print("=================================\n")

        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_role'] = user.get('role', 'user')
            session['user_profile_image'] = user.get('profile_image')

            print("\n========== SESSION AFTER LOGIN ==========")
            print(dict(session))
            print("=========================================\n")

            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'danger')

    return render_template('login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    # If user is already logged in, redirect to dashboard
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        if create_user(name, email, hashed.decode('utf-8')):
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Email already exists', 'danger')

    return render_template('register.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))