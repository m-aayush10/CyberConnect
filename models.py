cat > models.py << 'EOF'
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
EOF