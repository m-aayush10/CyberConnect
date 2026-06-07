from db import mysql

def dict_fetchall(cursor):
    columns = [desc[0] for desc in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def dict_fetchone(cursor):
    row = cursor.fetchone()
    if row is None:
        return None
    columns = [desc[0] for desc in cursor.description]
    return dict(zip(columns, row))

def get_user_by_email(email):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = dict_fetchone(cur)
    cur.close()
    return user

def get_user_by_id(user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, name, email, bio, profile_image FROM users WHERE id = %s", (user_id,))
    user = dict_fetchone(cur)
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

def add_skill(user_id, skill_name, level='Beginner'):
    try:
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO skills (user_id, skill_name, level) VALUES (%s, %s, %s)",
                    (user_id, skill_name, level))
        mysql.connection.commit()
        cur.close()
        return True
    except Exception as e:
        print(e)
        return False

def get_user_skills(user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, skill_name, level FROM skills WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
    skills = dict_fetchall(cur)
    cur.close()
    return skills

def delete_skill(skill_id, user_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM skills WHERE id = %s AND user_id = %s", (skill_id, user_id))
    mysql.connection.commit()
    cur.close()

def add_certification(user_id, title, issuer, date_earned=None, credential_url=None):
    try:
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO certifications (user_id, title, issuer, date_earned, credential_url) VALUES (%s, %s, %s, %s, %s)",
                    (user_id, title, issuer, date_earned, credential_url))
        mysql.connection.commit()
        cur.close()
        return True
    except Exception as e:
        print(e)
        return False

def get_user_certifications(user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, title, issuer, date_earned, credential_url FROM certifications WHERE user_id = %s ORDER BY date_earned DESC", (user_id,))
    certs = dict_fetchall(cur)
    cur.close()
    return certs

def delete_certification(cert_id, user_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM certifications WHERE id = %s AND user_id = %s", (cert_id, user_id))
    mysql.connection.commit()
    cur.close()

def update_profile_picture(user_id, profile_image):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE users SET profile_image = %s WHERE id = %s", (profile_image, user_id))
    mysql.connection.commit()
    cur.close()

def get_user_post_count(user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(*) FROM posts WHERE user_id = %s", (user_id,))
    count = cur.fetchone()[0]
    cur.close()
    return count

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
    count = cur.fetchone()[0]
    cur.close()
    return count

def get_following_count(user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(*) FROM followers WHERE follower_id = %s", (user_id,))
    count = cur.fetchone()[0]
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
    rows = cur.fetchall()
    cur.close()
    
    followers = []
    for row in rows:
        followers.append({
            'id': row[0],
            'name': row[1],
            'profile_image': row[2]
        })
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
    rows = cur.fetchall()
    cur.close()
    
    following = []
    for row in rows:
        following.append({
            'id': row[0],
            'name': row[1],
            'profile_image': row[2]
        })
    return following
