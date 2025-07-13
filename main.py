from flask import Flask, render_template, request, session, jsonify, redirect
import requests
import os
import sqlite3

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'fallback-secret')

PAID_USERS = [
    "paid_user@example.com",
    "premium_user@example.com",
    "+1234567890"
]

@app.route('/home')
def home():
    if 'user_email' not in session:
        return redirect('/login')

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, email_text, created_at 
        FROM emails 
        WHERE user_email = ? AND is_archived = 0 AND is_locked = 0
        ORDER BY created_at DESC
    """, (session['user_email'],))
    emails = cursor.fetchall()
    conn.close()

    return render_template('home.html', emails=emails)

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/generate email')
def index():
    if 'user_email' not in session:
        return redirect('/login')
    return render_template('index.html')

@app.route('/profile')
def profile():
    if 'user_email' not in session:
        return redirect('/login')
    
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    
    # Get total emails
    cursor.execute("SELECT COUNT(*) FROM emails WHERE user_email = ?", (session['user_email'],))
    total_emails = cursor.fetchone()[0]
    
    # Get archived emails
    cursor.execute("SELECT COUNT(*) FROM emails WHERE user_email = ? AND is_archived = 1", (session['user_email'],))
    archived_emails = cursor.fetchone()[0]
    
    # Get locked emails
    cursor.execute("SELECT COUNT(*) FROM emails WHERE user_email = ? AND is_locked = 1", (session['user_email'],))
    locked_emails = cursor.fetchone()[0]
    
    # Get active emails (non-archived, non-locked)
    cursor.execute("SELECT COUNT(*) FROM emails WHERE user_email = ? AND is_archived = 0 AND is_locked = 0", (session['user_email'],))
    active_emails = cursor.fetchone()[0]
    
    conn.close()
    
    return render_template('profile.html', 
                         total_emails=total_emails,
                         archived_emails=archived_emails,
                         locked_emails=locked_emails,
                         active_emails=active_emails)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email').strip()
        password = request.form.get('password').strip()

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()

        if user and user[2] == password:
            session['user_email'] = email
            session['is_paid'] = bool(user[3])
            session['email_count'] = 0
            return redirect('/generate email')
        else:
            return "❌ Invalid credentials. <a href='/login'>Try again</a> or <a href='/signup'>sign up</a>."

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email').strip()
        password = request.form.get('password').strip()

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            conn.close()
            return "❌ Email already registered. <a href='/login'>Login instead</a>"

        cursor.execute("INSERT INTO users (email, password, is_paid) VALUES (?, ?, ?)", (email, password, 0))
        conn.commit()
        conn.close()

        return redirect('/login')

    return render_template('signup.html')

@app.route('/generate', methods=['POST'])
def generate_email():
    try:
        user_id = request.form.get('user_id', '').strip()
        service = request.form.get('service', '').strip()
        client_type = request.form.get('client_type', '').strip()
        tone = request.form.get('tone', 'professional')
        length = request.form.get('length', 'medium').strip()
        word_limit = request.form.get('word_limit', '').strip()

        if not all([user_id, service, client_type]):
            return jsonify({'error': 'Please fill in all required fields.'}), 400

        word_limit = int(word_limit) if word_limit.isdigit() else {'short': 75, 'medium': 150, 'long': 250}.get(length, 150)

        if 'email_count' not in session:
            session['email_count'] = 0
        if 'user_id' not in session:
            session['user_id'] = user_id
        if session.get('user_id') != user_id:
            session['user_id'] = user_id
            session['email_count'] = 0

        is_paid_user = user_id in PAID_USERS

        prompt = f"Write a cold email in {tone} tone with about {word_limit} words from a freelancer offering '{service}' to a {client_type}."

        headers = {
            "Authorization": f"Bearer {os.getenv('TOGETHER_API_KEY')}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": int(word_limit * 1.3)
        }

        response = requests.post("https://api.together.xyz/v1/chat/completions", headers=headers, json=data, timeout=30)
        if response.status_code == 200:
            generated_email = response.json()['choices'][0]['message']['content'].strip()
            conn = sqlite3.connect("users.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO emails (user_email, email_text) VALUES (?, ?)", (session.get('user_email'), generated_email))
            conn.commit()
            conn.close()
            if not is_paid_user:
                session['email_count'] += 1
            return jsonify({'success': True, 'email': generated_email, 'remaining_free': 0 if is_paid_user else max(0, 1 - session['email_count']), 'is_paid_user': is_paid_user})
        return jsonify({'error': f'API Error: {response.status_code} - {response.text}'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/delete/<int:email_id>', methods=['POST'])
def delete_email(email_id):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM emails WHERE id = ? AND user_email = ?", (email_id, session.get('user_email')))
    conn.commit()
    conn.close()
    return redirect('/home')

@app.route('/delete_all', methods=['POST'])
def delete_all_emails():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM emails WHERE user_email = ?", (session.get('user_email'),))
    conn.commit()
    conn.close()
    return redirect('/home')

@app.route('/archive/<int:email_id>', methods=['POST'])
def archive_email(email_id):
    if 'user_email' not in session:
        return redirect('/login')

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE emails SET is_archived = 1 WHERE id = ? AND user_email = ?", (email_id, session['user_email']))
    conn.commit()
    conn.close()
    return redirect('/home')

@app.route('/archived')
def view_archived():
    if 'user_email' not in session:
        return redirect('/login')

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, email_text, created_at FROM emails WHERE user_email = ? AND is_archived = 1 ORDER BY created_at DESC", (session['user_email'],))
    emails = cursor.fetchall()
    conn.close()
    return render_template('archived.html', emails=emails)

@app.route('/unarchive/<int:email_id>', methods=['POST'])
def unarchive_email(email_id):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE emails SET is_archived = 0 WHERE id = ? AND user_email = ?", (email_id, session['user_email']))
    conn.commit()
    conn.close()
    return redirect('/archived')

@app.route('/delete_archived/<int:email_id>', methods=['POST'])
def delete_archived_email(email_id):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM emails WHERE id = ? AND user_email = ? AND is_archived = 1", (email_id, session['user_email']))
    conn.commit()
    conn.close()
    return redirect('/archived')

@app.route('/delete_all_archived', methods=['POST'])
def delete_all_archived():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM emails WHERE user_email = ? AND is_archived = 1", (session['user_email'],))
    conn.commit()
    conn.close()
    return redirect('/archived')

@app.route('/set_lock_password', methods=['GET', 'POST'])
def set_lock_password():
    if 'user_email' not in session:
        return redirect('/login')

    if request.method == 'POST':
        password = request.form.get('password').strip()
        if not password:
            return "⚠️ Password cannot be empty. <a href='/set_lock_password'>Try again</a>"

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET lock_password = ? WHERE email = ?", (password, session['user_email']))
        conn.commit()
        conn.close()

        return redirect('/locked')

    return render_template('set_lock_password.html')

@app.route('/locked', methods=['GET', 'POST'])
def locked_emails():
    if 'user_email' not in session:
        return redirect('/login')

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT lock_password FROM users WHERE email = ?", (session['user_email'],))
    result = cursor.fetchone()

    if not result:
        conn.close()
        return redirect('/login')  # user doesn't exist

    lock_password = result[0]

    if not lock_password:
        conn.close()
        return redirect('/set_lock_password')  # first-time password setup

    if request.method == 'POST':
        entered_password = request.form.get('password', '').strip()
        if entered_password == lock_password:
            cursor.execute("SELECT id, email_text, created_at FROM emails WHERE user_email = ? AND is_locked = 1 ORDER BY created_at DESC", (session['user_email'],))
            emails = cursor.fetchall()
            conn.close()
            return render_template('locked.html', emails=emails)
        else:
            conn.close()
            return render_template('verify_lock_password.html', error="Incorrect password")  # ✅ Proper error handling

    conn.close()
    return render_template('verify_lock_password.html')  # Show form


@app.route('/lock/<int:email_id>', methods=['POST'])
def lock_email(email_id):
    if 'user_email' not in session:
        return redirect('/login')

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE emails SET is_locked = 1 WHERE id = ? AND user_email = ?", (email_id, session['user_email']))
    conn.commit()
    conn.close()
    return redirect('/home')

@app.route('/forgot_lock_password', methods=['GET', 'POST'])
def forgot_lock_password():
    if 'user_email' not in session:
        return redirect('/login')

    if request.method == 'POST':
        account_password = request.form.get('account_password').strip()

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE email = ?", (session['user_email'],))
        real_password = cursor.fetchone()[0]

        if account_password == real_password:
            conn.close()
            return redirect('/set_lock_password')
        else:
            conn.close()
            
    return "❌ Incorrect lock password. <a href='/locked'>Try again</a> or <a href='/forgot_lock_password'>Reset it</a>"

@app.route('/unlock/<int:email_id>', methods=['POST'])
def unlock_email(email_id):
    if 'user_email' not in session:
        return redirect('/login')
    
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE emails SET is_locked = 0 WHERE id = ? AND user_email = ?", (email_id, session['user_email']))
    conn.commit()
    conn.close()
    return redirect('/locked')

@app.route('/delete_locked/<int:email_id>', methods=['POST'])
def delete_locked_email(email_id):
    if 'user_email' not in session:
        return redirect('/login')
    
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM emails WHERE id = ? AND user_email = ? AND is_locked = 1", (email_id, session['user_email']))
    conn.commit()
    conn.close()
    return redirect('/locked')

@app.route('/change_password', methods=['POST'])
def change_password():
    if 'user_email' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401
    
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    
    if not current_password or not new_password:
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400
    
    if len(new_password) < 6:
        return jsonify({'success': False, 'error': 'New password must be at least 6 characters'}), 400
    
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE email = ?", (session['user_email'],))
    result = cursor.fetchone()
    
    if not result or result[0] != current_password:
        conn.close()
        return jsonify({'success': False, 'error': 'Current password is incorrect'}), 400
    
    cursor.execute("UPDATE users SET password = ? WHERE email = ?", (new_password, session['user_email']))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Password changed successfully'})

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


    


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
