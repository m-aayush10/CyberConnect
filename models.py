from db import mysql

def get_user_by_email(email):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cur.fetchone()
    columns = [desc[0] for desc in cur.description] if user else None
    cur.close()
    if user:
        return dict(zip(columns, user))
    return None

def get_user_by_id(user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, name, email, bio, profile_image, cover_photo FROM users WHERE id = %s", (user_id,))
    user = cur.fetchone()
    columns = [desc[0] for desc in cur.description] if user else None
    cur.close()
    if user:
        return dict(zip(columns, user))
    return None

def create_user(name, email, hashed_password):
    try:
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, hashed_password))
        mysql.connection.commit()
        cur.close()
        return True
    except Exception:
        return False

def update_user_profile(user_id, name=None, bio=None, profile_image=None):
    cur = mysql.connection.cursor()
    if name:
        cur.execute("UPDATE users SET name = %s WHERE id = %s", (name, user_id))
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

def get_user_post_count(user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(*) FROM posts WHERE user_id = %s", (user_id,))
    count = cur.fetchone()[0]
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
    rows = cur.fetchall()
    cur.close()
    
    posts = []
    for row in rows:
        posts.append({
            'id': row[0],
            'user_id': row[1],
            'content': row[2],
            'image_url': row[3],
            'created_at': row[4],
            'name': row[5]
        })
    return posts

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
    rows = cur.fetchall()
    cur.close()
    
    if not rows:
        return []
    
    skills = []
    for row in rows:
        skills.append({
            'id': row[0],
            'skill_name': row[1],
            'level': row[2]
        })
    return skills

def delete_skill(skill_id, user_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM skills WHERE id = %s AND user_id = %s", (skill_id, user_id))
    mysql.connection.commit()
    cur.close()

def get_skill_by_id(skill_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM skills WHERE id = %s", (skill_id,))
    row = cur.fetchone()
    cur.close()
    if row:
        return {
            'id': row[0],
            'user_id': row[1],
            'skill_name': row[2],
            'level': row[3]
        }
    return None

def update_skill(skill_id, skill_name, level):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE skills SET skill_name = %s, level = %s WHERE id = %s",
                (skill_name, level, skill_id))
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
    except Exception:
        return False

def get_user_certifications(user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, title, issuer, date_earned, credential_url FROM certifications WHERE user_id = %s ORDER BY date_earned DESC", (user_id,))
    rows = cur.fetchall()
    cur.close()
    
    if not rows:
        return []
    
    certs = []
    for row in rows:
        certs.append({
            'id': row[0],
            'title': row[1],
            'issuer': row[2],
            'date_earned': row[3],
            'credential_url': row[4]
        })
    return certs

def delete_certification(cert_id, user_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM certifications WHERE id = %s AND user_id = %s", (cert_id, user_id))
    mysql.connection.commit()
    cur.close()

def get_certification_by_id(cert_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM certifications WHERE id = %s", (cert_id,))
    row = cur.fetchone()
    cur.close()
    if row:
        return {
            'id': row[0],
            'user_id': row[1],
            'title': row[2],
            'issuer': row[3],
            'date_earned': row[4],
            'credential_url': row[5]
        }
    return None

def update_certification(cert_id, title, issuer, date_earned=None, credential_url=None):
    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE certifications 
        SET title = %s, issuer = %s, date_earned = %s, credential_url = %s 
        WHERE id = %s
    """, (title, issuer, date_earned, credential_url, cert_id))
    mysql.connection.commit()
    cur.close()

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
    count = cur.fetchone()[0]
    cur.close()
    return count

def user_has_liked(user_id, post_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT 1 FROM likes WHERE user_id = %s AND post_id = %s", (user_id, post_id))
    result = cur.fetchone()
    cur.close()
    return result is not None

def add_comment(user_id, post_id, content):
    try:
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO comments (user_id, post_id, content) VALUES (%s, %s, %s)", 
                    (user_id, post_id, content))
        mysql.connection.commit()
        cur.close()
        return True
    except Exception:
        return False

def get_comments_by_post(post_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT comments.*, users.name, users.profile_image 
        FROM comments 
        JOIN users ON comments.user_id = users.id 
        WHERE comments.post_id = %s 
        ORDER BY comments.created_at ASC
    """, (post_id,))
    rows = cur.fetchall()
    cur.close()
    
    comments = []
    for row in rows:
        comments.append({
            'id': row[0],
            'user_id': row[1],
            'post_id': row[2],
            'content': row[3],
            'created_at': row[4],
            'name': row[5],
            'profile_image': row[6]
        })
    return comments

def delete_comment(comment_id, user_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM comments WHERE id = %s AND user_id = %s", (comment_id, user_id))
    mysql.connection.commit()
    cur.close()

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
    
    if not rows:
        return []
    
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
    
    if not rows:
        return []
    
    following = []
    for row in rows:
        following.append({
            'id': row[0],
            'name': row[1],
            'profile_image': row[2]
        })
    return following

# ============================================================
#  ADMIN FUNCTIONS
# ============================================================

def get_all_users():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, name, email, role, created_at FROM users ORDER BY created_at DESC")
    rows = cur.fetchall()
    cur.close()
    users = []
    for row in rows:
        users.append({
            'id': row[0],
            'name': row[1],
            'email': row[2],
            'role': row[3],
            'created_at': row[4]
        })
    return users

def get_all_posts():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT posts.id, posts.content, posts.created_at, users.name as author
        FROM posts
        JOIN users ON posts.user_id = users.id
        ORDER BY posts.created_at DESC
    """)
    rows = cur.fetchall()
    cur.close()
    posts = []
    for row in rows:
        posts.append({
            'id': row[0],
            'content': row[1],
            'created_at': row[2],
            'author': row[3]
        })
    return posts

def delete_user(user_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
    mysql.connection.commit()
    cur.close()

def delete_post_by_admin(post_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM posts WHERE id = %s", (post_id,))
    mysql.connection.commit()
    cur.close()

# SELF-DELETE ACCOUNT (Complete User CRUD)
def delete_user_by_id(user_id):
    """Delete a user and ALL their related data"""
    cur = mysql.connection.cursor()
    
    cur.execute("DELETE FROM comments WHERE user_id = %s", (user_id,))
    cur.execute("DELETE FROM likes WHERE user_id = %s", (user_id,))
    cur.execute("DELETE FROM followers WHERE follower_id = %s OR followed_id = %s", (user_id, user_id))
    cur.execute("DELETE FROM certifications WHERE user_id = %s", (user_id,))
    cur.execute("DELETE FROM skills WHERE user_id = %s", (user_id,))
    cur.execute("DELETE FROM posts WHERE user_id = %s", (user_id,))
    cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
    
    mysql.connection.commit()
    cur.close()

# EDIT COMMENT 
def get_comment_by_id(comment_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, user_id, post_id, content, created_at FROM comments WHERE id = %s", (comment_id,))
    row = cur.fetchone()
    cur.close()
    if row:
        return {
            'id': row[0],
            'user_id': row[1],
            'post_id': row[2],
            'content': row[3],
            'created_at': row[4]
        }
    return None

def update_comment(comment_id, content):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE comments SET content = %s WHERE id = %s", (content, comment_id))
    mysql.connection.commit()
    cur.close()

def search_users(query, current_user_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT id, name, email, profile_image 
        FROM users 
        WHERE (name LIKE %s OR email LIKE %s) AND id != %s
        ORDER BY name ASC
    """, (f'%{query}%', f'%{query}%', current_user_id))
    rows = cur.fetchall()
    cur.close()
    results = []
    for row in rows:
        results.append({
            'id': row[0],
            'name': row[1],
            'email': row[2],
            'profile_image': row[3]
        })
    return results

def get_suggested_users(current_user_id, limit=5):
    """Get users that the current user is not following (excluding self)"""
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT id, name, email, profile_image 
        FROM users 
        WHERE id != %s 
        AND id NOT IN (
            SELECT followed_id FROM followers WHERE follower_id = %s
        )
        ORDER BY RAND()
        LIMIT %s
    """, (current_user_id, current_user_id, limit))
    rows = cur.fetchall()
    cur.close()
    
    suggestions = []
    for row in rows:
        suggestions.append({
            'id': row[0],
            'name': row[1],
            'email': row[2],
            'profile_image': row[3]
        })
    return suggestions

# NOTIFICATIONS FUNCTIONS


def create_notification(user_id, actor_id, type, content, post_id=None, comment_id=None):
    """Create a new notification"""
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO notifications (user_id, actor_id, type, content, post_id, comment_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user_id, actor_id, type, content, post_id, comment_id))
        mysql.connection.commit()
        cur.close()
        return True
    except Exception as e:
        print(f"Notification error: {e}")
        return False

def get_notifications(user_id, limit=10):
    """Get notifications for a user (most recent first)"""
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT n.*, u.name as actor_name, u.profile_image as actor_image
        FROM notifications n
        JOIN users u ON n.actor_id = u.id
        WHERE n.user_id = %s
        ORDER BY n.created_at DESC
        LIMIT %s
    """, (user_id, limit))
    rows = cur.fetchall()
    cur.close()
    
    notifications = []
    for row in rows:
        notifications.append({
            'id': row[0],
            'user_id': row[1],
            'actor_id': row[2],
            'type': row[3],
            'content': row[4],
            'post_id': row[5],
            'comment_id': row[6],
            'is_read': row[7],
            'created_at': row[8],
            'actor_name': row[9],
            'actor_image': row[10]
        })
    return notifications

def get_unread_count(user_id):
    """Get count of unread notifications"""
    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(*) FROM notifications WHERE user_id = %s AND is_read = FALSE", (user_id,))
    count = cur.fetchone()[0]
    cur.close()
    return count

def mark_notification_read(notification_id, user_id):
    """Mark a single notification as read"""
    cur = mysql.connection.cursor()
    cur.execute("UPDATE notifications SET is_read = TRUE WHERE id = %s AND user_id = %s", (notification_id, user_id))
    mysql.connection.commit()
    cur.close()

def mark_all_notifications_read(user_id):
    """Mark all notifications as read for a user"""
    cur = mysql.connection.cursor()
    cur.execute("UPDATE notifications SET is_read = TRUE WHERE user_id = %s", (user_id,))
    mysql.connection.commit()
    cur.close()

# ============================================================
# NOTIFICATIONS FUNCTIONS
# ============================================================

def create_notification(user_id, actor_id, type, content, post_id=None, comment_id=None):
    """Create a new notification"""
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO notifications (user_id, actor_id, type, content, post_id, comment_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user_id, actor_id, type, content, post_id, comment_id))
        mysql.connection.commit()
        cur.close()
        return True
    except Exception as e:
        print(f"Notification error: {e}")
        return False

def get_notifications(user_id, limit=10):
    """Get notifications for a user (most recent first)"""
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT n.*, u.name as actor_name, u.profile_image as actor_image
        FROM notifications n
        JOIN users u ON n.actor_id = u.id
        WHERE n.user_id = %s
        ORDER BY n.created_at DESC
        LIMIT %s
    """, (user_id, limit))
    rows = cur.fetchall()
    cur.close()
    
    notifications = []
    for row in rows:
        notifications.append({
            'id': row[0],
            'user_id': row[1],
            'actor_id': row[2],
            'type': row[3],
            'content': row[4],
            'post_id': row[5],
            'comment_id': row[6],
            'is_read': row[7],
            'created_at': row[8],
            'actor_name': row[9],
            'actor_image': row[10]
        })
    return notifications

def get_unread_count(user_id):
    """Get count of unread notifications"""
    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(*) FROM notifications WHERE user_id = %s AND is_read = FALSE", (user_id,))
    count = cur.fetchone()[0]
    cur.close()
    return count

def mark_notification_read(notification_id, user_id):
    """Mark a single notification as read"""
    cur = mysql.connection.cursor()
    cur.execute("UPDATE notifications SET is_read = TRUE WHERE id = %s AND user_id = %s", (notification_id, user_id))
    mysql.connection.commit()
    cur.close()

def mark_all_notifications_read(user_id):
    """Mark all notifications as read for a user"""
    cur = mysql.connection.cursor()
    cur.execute("UPDATE notifications SET is_read = TRUE WHERE user_id = %s", (user_id,))
    mysql.connection.commit()
    cur.close()

# ============================================================
# REPOST FUNCTIONS
# ============================================================

def create_repost(user_id, original_post_id, content=None):
    """Create a repost of an existing post"""
    try:
        cur = mysql.connection.cursor()
        # Check if already reposted
        cur.execute("SELECT id FROM reposts WHERE user_id = %s AND original_post_id = %s", (user_id, original_post_id))
        if cur.fetchone():
            cur.close()
            return False
        
        cur.execute("""
            INSERT INTO reposts (user_id, original_post_id, content)
            VALUES (%s, %s, %s)
        """, (user_id, original_post_id, content))
        mysql.connection.commit()
        cur.close()
        
        # Create notification for post owner
        cur = mysql.connection.cursor()
        cur.execute("SELECT user_id FROM posts WHERE id = %s", (original_post_id,))
        post_owner = cur.fetchone()
        cur.close()
        
        if post_owner and post_owner[0] != user_id:
            from flask import session
            actor_name = session.get('user_name', 'Someone')
            create_notification(
                user_id=post_owner[0],
                actor_id=user_id,
                type='repost',
                content=f"{actor_name} reposted your post",
                post_id=original_post_id
            )
        
        return True
    except Exception as e:
        print(f"Repost error: {e}")
        return False

def get_repost_count(post_id):
    """Get number of reposts for a post"""
    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(*) FROM reposts WHERE original_post_id = %s", (post_id,))
    count = cur.fetchone()[0]
    cur.close()
    return count

def user_has_reposted(user_id, post_id):
    """Check if user has reposted a post"""
    cur = mysql.connection.cursor()
    cur.execute("SELECT id FROM reposts WHERE user_id = %s AND original_post_id = %s", (user_id, post_id))
    result = cur.fetchone()
    cur.close()
    return result is not None

def get_reposts_by_user(user_id):
    """Get all reposts by a user"""
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT r.*, p.content as original_content, p.user_id as original_author_id, u.name as original_author_name
        FROM reposts r
        JOIN posts p ON r.original_post_id = p.id
        JOIN users u ON p.user_id = u.id
        WHERE r.user_id = %s
        ORDER BY r.created_at DESC
    """, (user_id,))
    rows = cur.fetchall()
    cur.close()
    reposts = []
    for row in rows:
        reposts.append({
            'id': row[0],
            'user_id': row[1],
            'original_post_id': row[2],
            'content': row[3],
            'created_at': row[4],
            'original_content': row[5],
            'original_author_id': row[6],
            'original_author_name': row[7]
        })
    return reposts

def get_profile_completion(user_id):
    """Calculate profile completion percentage"""
    user = get_user_by_id(user_id)
    if not user:
        return 0
    
    total_items = 5
    completed = 0
    
    # Profile picture
    if user.get('profile_image') and user['profile_image']:
        completed += 1
    
    # Cover photo
    if user.get('cover_photo') and user['cover_photo']:
        completed += 1
    
    # Bio
    if user.get('bio') and len(user['bio'].strip()) > 0:
        completed += 1
    
    # Skills
    from models import get_user_skills
    skills = get_user_skills(user_id)
    if skills and len(skills) > 0:
        completed += 1
    
    # Certifications
    from models import get_user_certifications
    certs = get_user_certifications(user_id)
    if certs and len(certs) > 0:
        completed += 1
    
    return int((completed / total_items) * 100)