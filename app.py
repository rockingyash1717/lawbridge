from flask import Flask, request, jsonify, render_template, send_file, session, redirect, url_for
from flask_cors import CORS
from chatbot.main import process_chat
from functools import wraps
import firebase_admin
from firebase_admin import credentials, firestore, auth
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app)
app.secret_key = os.urandom(24)  # for session management

# Load environment variables
load_dotenv()

# Initialize Firebase Admin SDK
cred = credentials.Certificate(os.path.join(os.path.dirname(__file__), 'firebase-service-account.json'))
firebase_admin.initialize_app(cred)
db = firestore.client()

# Admin credentials (in a real application, these should be stored securely)
ADMIN_EMAIL = "admin"
ADMIN_PASSWORD = "pass"  # In production, use a strong hashed password

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin' not in session:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# Admin routes
@app.route("/api/auth/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "GET":
        return render_template("admin_login.html")
    
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
        session['admin'] = True
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "Invalid credentials"}), 401

@app.route("/api/auth/admin/logout", methods=["POST"])
def admin_logout():
    session.pop('admin', None)
    return jsonify({"success": True})

@app.route("/api/admin/dashboard")
@admin_required
def admin_dashboard():
    return render_template("admin.html")

@app.route("/api/admin/dashboard-data")
@admin_required
def admin_dashboard_data():
    try:
        # Get all users
        users_ref = db.collection('users').stream()
        users = []
        total_users = 0
        active_today = 0
        total_chats = 0
        
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        
        for user in users_ref:
            user_data = user.to_dict()
            user_data['id'] = user.id
            
            # Count active users
            last_login = user_data.get('last_login')
            if last_login and last_login.date() >= yesterday.date():
                active_today += 1
            
            # Get chat count for user
            chats = db.collection('chats').document(user.id).collection('messages').count().get()
            user_data['total_chats'] = chats[0][0].value
            total_chats += user_data['total_chats']
            
            users.append(user_data)
            total_users += 1
        
        return jsonify({
            "success": True,
            "users": users,
            "totalUsers": total_users,
            "activeToday": active_today,
            "totalChats": total_chats
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/auth/config")
def firebase_config():
    config = {
        "apiKey": os.getenv('FIREBASE_API_KEY'),
        "authDomain": os.getenv('FIREBASE_AUTH_DOMAIN'),
        "projectId": os.getenv('FIREBASE_PROJECT_ID'),
        "storageBucket": os.getenv('FIREBASE_STORAGE_BUCKET'),
        "messagingSenderId": os.getenv('FIREBASE_MESSAGING_SENDER_ID'),
        "appId": os.getenv('FIREBASE_APP_ID')
    }
    return jsonify(config)

@app.route("/api/auth/login", methods=["GET"])
def login():
    if 'user_id' in session:
        return redirect(url_for('chat'))
    return render_template("login.html")

@app.route("/api/auth/verify-token", methods=["POST"])
def verify_token():
    try:
        id_token = request.json.get('idToken')
        if not id_token:
            raise ValueError("No token provided")

        # Verify the Firebase ID token
        decoded_token = auth.verify_id_token(id_token)
        user_id = decoded_token['uid']
        
        # Store user info in Firestore if new user
        user_ref = db.collection('users').document(user_id)
        if not user_ref.get().exists:
            user_data = {
                'email': decoded_token.get('email', ''),
                'name': decoded_token.get('name', ''),
                'created_at': datetime.now(),
                'last_login': datetime.now()
            }
            user_ref.set(user_data)
        else:
            # Update last login time
            user_ref.update({'last_login': datetime.now()})

        # Set session
        session['user_id'] = user_id
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 401

@app.route("/api/auth/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"success": True})

@app.route("/api/chat", methods=["GET", "POST"])
@login_required
def chat():
    if request.method == "GET":
        return render_template("chat.html")
    else:
        data = request.json
        user_input = data.get("message")
        response = process_chat(user_input)
        
        # Save chat message to Firestore
        chat_ref = db.collection('chats').document(session['user_id']).collection('messages')
        chat_ref.add({
            'user_message': user_input,
            'bot_response': response,
            'timestamp': datetime.now(),
            'session_id': session.get('chat_session_id', datetime.now().strftime('%Y%m%d%H%M%S'))
        })
        
        return jsonify({
            "response": response
        })

@app.route("/chat/history")
@login_required
def chat_history_page():
    return render_template('history.html')

@app.route("/api/chat/history/data")
@login_required
def chat_history_data():
    try:
        # Get chat messages from Firestore
        chat_ref = db.collection('chats').document(session['user_id']).collection('messages')
        messages = chat_ref.order_by('timestamp', direction=firestore.Query.DESCENDING).stream()
        
        # Group messages by session
        sessions = {}
        for msg in messages:
            data = msg.to_dict()
            session_id = data['session_id']
            if session_id not in sessions:
                sessions[session_id] = {
                    'timestamp': data['timestamp'],
                    'messages': []
                }
            sessions[session_id]['messages'].extend([
                {
                    'role': 'user',
                    'content': data['user_message'],
                    'timestamp': data['timestamp']
                },
                {
                    'role': 'bot',
                    'content': data['bot_response'],
                    'timestamp': data['timestamp']
                }
            ])
        
        # Convert to list and sort by timestamp
        history = [
            {
                'timestamp': session['timestamp'],
                'messages': sorted(session['messages'], key=lambda x: x['timestamp'])
            }
            for session in sessions.values()
        ]
        history.sort(key=lambda x: x['timestamp'], reverse=True)
        return jsonify({"history": history})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/profile")
@login_required
def profile():
    try:
        user_ref = db.collection('users').document(session['user_id'])
        user_doc = user_ref.get()
        user_data = user_doc.to_dict()
        
        # Get chat statistics
        chat_ref = db.collection('chats').document(session['user_id']).collection('messages')
        
        # Total chats
        total_chats = chat_ref.count().get()[0][0].value
        
        # Chats today
        today = datetime.now().date()
        today_start = datetime.combine(today, datetime.min.time())
        chats_today = chat_ref.where('timestamp', '>=', today_start).count().get()[0][0].value
        
        # Average response time (simplified)
        avg_response_time = 2.5  # Placeholder - implement actual calculation if needed
        
        # Get or initialize user preferences
        if 'preferences' not in user_data:
            user_data['preferences'] = {
                'language': 'en',
                'email_notifications': True,
                'sound_enabled': True,
                'theme': 'default'
            }
        
        return render_template('profile.html',
                             user=user_data,
                             total_chats=total_chats,
                             chats_today=chats_today,
                             avg_response_time=avg_response_time)
    except Exception as e:
        print(f"Error in profile route: {e}")
        return redirect(url_for('login'))

@app.route("/api/profile/preferences", methods=["POST"])
@login_required
def update_preferences():
    try:
        preferences = request.json
        user_ref = db.collection('users').document(session['user_id'])
        user_ref.update({
            'preferences': preferences
        })
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/")
def index():
    return redirect("/api/auth/login")

if __name__ == "__main__":
    app.run(debug=True)
