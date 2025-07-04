
from flask import Flask, render_template, request, session, jsonify
import requests
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'  # Change this in production

# Configuration
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY', 'your-api-key-here')
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# List of paid users (user IDs)
PAID_USERS = [
    "paid_user@example.com",
    "premium_user@example.com",
    "+1234567890"
]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_email():
    try:
        # Get form data
        user_id = request.form.get('user_id', '').strip()
        service = request.form.get('service', '').strip()
        client_type = request.form.get('client_type', '').strip()
        tone = request.form.get('tone', 'professional')
        
        # Validate inputs
        if not all([user_id, service, client_type]):
            return jsonify({
                'error': 'Please fill in all required fields.'
            }), 400
        
        # Initialize session if needed
        if 'email_count' not in session:
            session['email_count'] = 0
        if 'user_id' not in session:
            session['user_id'] = user_id
        
        # Check if user changed
        if session.get('user_id') != user_id:
            session['user_id'] = user_id
            session['email_count'] = 0
        
        # Check usage limits
        is_paid_user = user_id in PAID_USERS
        
        if not is_paid_user and session['email_count'] >= 1:
            return jsonify({
                'error': 'Free limit reached! Contact us on WhatsApp for unlimited access.',
                'payment_link': 'https://wa.me/1234567890?text=I%20want%20unlimited%20cold%20email%20generation'
            }), 403
        
        # Generate email using OpenRouter API
        prompt = f"Write a cold email for a freelancer offering {service} to a {client_type}. Tone: {tone}. Max 150 words."
        
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "openai/gpt-3.5-turbo",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 300,
            "temperature": 0.7
        }
        
        # Make API request
        response = requests.post(OPENROUTER_URL, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            generated_email = result['choices'][0]['message']['content'].strip()
            
            # Increment usage count for non-paid users
            if not is_paid_user:
                session['email_count'] += 1
            
            return jsonify({
                'success': True,
                'email': generated_email,
                'remaining_free': 0 if is_paid_user else max(0, 1 - session['email_count']),
                'is_paid_user': is_paid_user
            })
        else:
            return jsonify({
                'error': f'API Error: {response.status_code} - {response.text}'
            }), 500
            
    except requests.exceptions.RequestException as e:
        return jsonify({
            'error': f'Network error: {str(e)}'
        }), 500
    except Exception as e:
        return jsonify({
            'error': f'An error occurred: {str(e)}'
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
