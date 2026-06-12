from db import mysql

# ========== SAFE HELPER FUNCTIONS ==========
def safe_dict_fetchone(cursor):
    row = cursor.fetchone()
    if row is None:
        return None
    columns = [desc[0] for desc in cursor.description]
    return dict(zip(columns, row))

def safe_dict_fetchall(cursor):
    rows = cursor.fetchall()
    if not rows:
        return []
    columns = [desc[0] for desc in cursor.description]
    return [dict(zip(columns, row)) for row in rows]

def safe_count(cursor):
    result = cursor.fetchone()
    return result[0] if result else 0

# ========== USER FUNCTIONS ==========
def get_user_by_email(email):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = safe_dict_fetchone(cur)
    cur.close()
    return user

def get_user_by_id(user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, name, email, bio, profile_image, cover_photo FROM users WHERE id = %s", (user_id,))
    user = safe_dict_fetchone(cur)
    cur.close()
    return user

def create_user(name, email, hashed_password):
    try:
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, hashed_password))
        mysql.connection.commit()
        cur.close()
        return True
    except Exception:
        return False

def update_user_profile(user_id, bio=None, profile_image=None):
    cur = mysql.connection.cursor()
    if bio:
        cur.execute("UPDATE users SET bio = %s WHERE id = %s", (bio, user_id))
    if profile_image:
        cur.execute("UPDATE users SET profile_image = %s WHERE id = %s", (profile_image, user_id))
    mysql.connection.commit()
    cur.close()

def update_profile_picture(user_id, profile_image):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE users SET profile_image = %s WHERE id = %s", (profile_image, user_id))
    mysql.connection.commit()
    cur.close()

def update_cover_photo(user_id, cover_image):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE users SET cover_photo = %s WHERE id = %s", (cover_image, user_id))
    mysql.connection.commit()
    cur.close()

# ========== SKILLS FUNCTIONS ==========
def add_skill(user_id, skill_name, level='Beginner'):
    try:
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO skills (user_id, skill_name, level) VALUES (%s, %s, %s)",
                    (user_id, skill_name, level))
        mysql.connection.commit()
        cur.close()
        return True
    except Exception:
        return False

def get_user_skills(user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, skill_name, level FROM skills WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
    skills = safe_dict_fetchall(cur)
    cur.close()
    return skills

def delete_skill(skill_id, user_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM skills WHERE id = %s AND user_id = %s", (skill_id, user_id))
    mysql.connection.commit()
    cur.close()

# ========== CERTIFICATIONS FUNCTIONS ==========
def add_certification(user_id, title, issuer, date_earned=None, credential_url=None):
    try:
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO certifications (user_id, title, issuer, date_earned, credential_url) VALUES (%s, %s, %s, %s, %s)",
                    (user_id, title, issuer, date_earned, credential_url))
        mysql.connection.commit()
        cur.close()
        return True
    except Exception:
        return False

def get_user_certifications(user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, title, issuer, date_earned, credential_url FROM certifications WHERE user_id = %s ORDER BY date_earned DESC", (user_id,))
    certs = safe_dict_fetchall(cur)
    cur.close()
    return certs

def delete_certification(cert_id, user_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM certifications WHERE id = %s AND user_id = %s", (cert_id, user_id))
    mysql.connection.commit()
    cur.close()

# ========== POSTS FUNCTIONS ==========
def get_user_post_count(user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(*) FROM posts WHERE user_id = %s", (user_id,))
    count = safe_count(cur)
    cur.close()
    return count

def get_user_posts(user_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT posts.*, users.name 
        FROM posts 
        JOIN users ON posts.user_id = users.id 
        WHERE posts.user_id = %s
        ORDER BY posts.created_at DESC
    """, (user_id,))
    posts = safe_dict_fetchall(cur)
    cur.close()
    return posts

# ========== FOLLOWERS/CONNECTIONS FUNCTIONS ==========
def follow_user(follower_id, followed_id):
    if follower_id == followed_id:
        return False
    try:
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO followers (follower_id, followed_id) VALUES (%s, %s)", 
                    (follower_id, followed_id))
        mysql.connection.commit()
        cur.close()
        return True
    except:
        return False

def unfollow_user(follower_id, followed_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM followers WHERE follower_id = %s AND followed_id = %s", 
                (follower_id, followed_id))
    mysql.connection.commit()
    cur.close()
    return True

def get_follower_count(user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(*) FROM followers WHERE followed_id = %s", (user_id,))
    count = safe_count(cur)
    cur.close()
    return count

def get_following_count(user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(*) FROM followers WHERE follower_id = %s", (user_id,))
    count = safe_count(cur)
    cur.close()
    return count

def is_following(follower_id, followed_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT 1 FROM followers WHERE follower_id = %s AND followed_id = %s", 
                (follower_id, followed_id))
    result = cur.fetchone()
    cur.close()
    return result is not None

def get_followers(user_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT users.id, users.name, users.profile_image 
        FROM followers 
        JOIN users ON followers.follower_id = users.id 
        WHERE followers.followed_id = %s
        ORDER BY followers.created_at DESC
    """, (user_id,))
    followers = safe_dict_fetchall(cur)
    cur.close()
    return followers

def get_following(user_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT users.id, users.name, users.profile_image 
        FROM followers 
        JOIN users ON followers.followed_id = users.id 
        WHERE followers.follower_id = %s
        ORDER BY followers.created_at DESC
    """, (user_id,))
    following = safe_dict_fetchall(cur)
    cur.close()
    return following
 
def add_like(user_id, post_id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO likes (user_id, post_id) VALUES (%s, %s)", (user_id, post_id))
        mysql.connection.commit()
        cur.close()
        return True
    except:
        return False

def remove_like(user_id, post_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM likes WHERE user_id = %s AND post_id = %s", (user_id, post_id))
    mysql.connection.commit()
    cur.close()
    return True

def get_like_count(post_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(*) FROM likes WHERE post_id = %s", (post_id,))
    result = cur.fetchone()
    cur.close()
    return result[0] if result else 0

def user_has_liked(user_id, post_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT 1 FROM likes WHERE user_id = %s AND post_id = %s", (user_id, post_id))
    result = cur.fetchone()
    cur.close()
    return result is not None