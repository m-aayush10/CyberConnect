from db import get_db

# ========== HELPER FUNCTIONS ==========

def dict_fetchone(row):
    if row is None:
        return None
    return dict(row)

def dict_fetchall(rows):
    return [dict(row) for row in rows]

# ========== USER FUNCTIONS ==========

def get_user_by_email(email):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    db.close()
    return dict_fetchone(user)

def get_user_by_id(user_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, name, email, bio, profile_image, cover_photo FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    db.close()
    return dict_fetchone(user)

def create_user(name, email, hashed_password):
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (name, email, hashed_password))
        db.commit()
        db.close()
        return True
    except Exception:
        return False

def update_user_profile(user_id, bio=None, profile_image=None):
    db = get_db()
    cursor = db.cursor()
    if bio:
        cursor.execute("UPDATE users SET bio = ? WHERE id = ?", (bio, user_id))
    if profile_image:
        cursor.execute("UPDATE users SET profile_image = ? WHERE id = ?", (profile_image, user_id))
    db.commit()
    db.close()

def update_profile_picture(user_id, profile_image):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("UPDATE users SET profile_image = ? WHERE id = ?", (profile_image, user_id))
    db.commit()
    db.close()

def update_cover_photo(user_id, cover_image):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("UPDATE users SET cover_photo = ? WHERE id = ?", (cover_image, user_id))
    db.commit()
    db.close()

def get_user_post_count(user_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM posts WHERE user_id = ?", (user_id,))
    count = cursor.fetchone()[0]
    db.close()
    return count

def get_user_posts(user_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT posts.*, users.name 
        FROM posts 
        JOIN users ON posts.user_id = users.id 
        WHERE posts.user_id = ?
        ORDER BY posts.created_at DESC
    """, (user_id,))
    posts = cursor.fetchall()
    db.close()
    return dict_fetchall(posts)

# ========== SKILLS FUNCTIONS ==========

def add_skill(user_id, skill_name, level='Beginner'):
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO skills (user_id, skill_name, level) VALUES (?, ?, ?)",
                       (user_id, skill_name, level))
        db.commit()
        db.close()
        return True
    except Exception:
        return False

def get_user_skills(user_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, skill_name, level FROM skills WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
    rows = cursor.fetchall()
    db.close()
    return dict_fetchall(rows)

def delete_skill(skill_id, user_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM skills WHERE id = ? AND user_id = ?", (skill_id, user_id))
    db.commit()
    db.close()

# ========== CERTIFICATIONS FUNCTIONS ==========

def add_certification(user_id, title, issuer, date_earned=None, credential_url=None):
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO certifications (user_id, title, issuer, date_earned, credential_url) 
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, title, issuer, date_earned, credential_url))
        db.commit()
        db.close()
        return True
    except Exception:
        return False

def get_user_certifications(user_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, title, issuer, date_earned, credential_url FROM certifications WHERE user_id = ? ORDER BY date_earned DESC", (user_id,))
    rows = cursor.fetchall()
    db.close()
    return dict_fetchall(rows)

def delete_certification(cert_id, user_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM certifications WHERE id = ? AND user_id = ?", (cert_id, user_id))
    db.commit()
    db.close()

def get_certification_by_id(cert_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM certifications WHERE id = ?", (cert_id,))
    cert = cursor.fetchone()
    db.close()
    return dict_fetchone(cert)

def update_certification(cert_id, title, issuer, date_earned=None, credential_url=None):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        UPDATE certifications 
        SET title = ?, issuer = ?, date_earned = ?, credential_url = ? 
        WHERE id = ?
    """, (title, issuer, date_earned, credential_url, cert_id))
    db.commit()
    db.close()

# ========== LIKES FUNCTIONS ==========

def add_like(user_id, post_id):
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO likes (user_id, post_id) VALUES (?, ?)", (user_id, post_id))
        db.commit()
        db.close()
        return True
    except:
        return False

def remove_like(user_id, post_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM likes WHERE user_id = ? AND post_id = ?", (user_id, post_id))
    db.commit()
    db.close()
    return True

def get_like_count(post_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM likes WHERE post_id = ?", (post_id,))
    count = cursor.fetchone()[0]
    db.close()
    return count

def user_has_liked(user_id, post_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT 1 FROM likes WHERE user_id = ? AND post_id = ?", (user_id, post_id))
    result = cursor.fetchone()
    db.close()
    return result is not None

# ========== COMMENTS FUNCTIONS ==========

def add_comment(user_id, post_id, content):
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO comments (user_id, post_id, content) VALUES (?, ?, ?)", 
                       (user_id, post_id, content))
        db.commit()
        db.close()
        return True
    except Exception:
        return False

def get_comments_by_post(post_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT comments.*, users.name, users.profile_image 
        FROM comments 
        JOIN users ON comments.user_id = users.id 
        WHERE comments.post_id = ? 
        ORDER BY comments.created_at ASC
    """, (post_id,))
    comments = cursor.fetchall()
    db.close()
    return dict_fetchall(comments)

def delete_comment(comment_id, user_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM comments WHERE id = ? AND user_id = ?", (comment_id, user_id))
    db.commit()
    db.close()

# ========== FOLLOWERS/CONNECTIONS FUNCTIONS ==========

def follow_user(follower_id, followed_id):
    if follower_id == followed_id:
        return False
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO followers (follower_id, followed_id) VALUES (?, ?)", 
                       (follower_id, followed_id))
        db.commit()
        db.close()
        return True
    except:
        return False

def unfollow_user(follower_id, followed_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM followers WHERE follower_id = ? AND followed_id = ?", 
                   (follower_id, followed_id))
    db.commit()
    db.close()
    return True

def get_follower_count(user_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM followers WHERE followed_id = ?", (user_id,))
    count = cursor.fetchone()[0]
    db.close()
    return count

def get_following_count(user_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM followers WHERE follower_id = ?", (user_id,))
    count = cursor.fetchone()[0]
    db.close()
    return count

def is_following(follower_id, followed_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT 1 FROM followers WHERE follower_id = ? AND followed_id = ?", 
                   (follower_id, followed_id))
    result = cursor.fetchone()
    db.close()
    return result is not None

def get_followers(user_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT users.id, users.name, users.profile_image 
        FROM followers 
        JOIN users ON followers.follower_id = users.id 
        WHERE followers.followed_id = ?
        ORDER BY followers.created_at DESC
    """, (user_id,))
    rows = cursor.fetchall()
    db.close()
    return dict_fetchall(rows)

def get_following(user_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT users.id, users.name, users.profile_image 
        FROM followers 
        JOIN users ON followers.followed_id = users.id 
        WHERE followers.follower_id = ?
        ORDER BY followers.created_at DESC
    """, (user_id,))
    rows = cursor.fetchall()
    db.close()
    return dict_fetchall(rows)