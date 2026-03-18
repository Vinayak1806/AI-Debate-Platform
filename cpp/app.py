import os
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import google.generativeai as genai
from datetime import date
from dotenv import load_dotenv
from db import get_db_connection

# Load .env from the same directory as app.py (cpp/) regardless of launch directory
_app_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(_app_dir, '.env'))

app = Flask(__name__)

# Secure Config Management: Get secret keys from environment variables
# Fallback keys are provided ONLY for development/demo purposes. In production, 
# you MUST set these environment variables and NEVER hardcode secrets.
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev_fallback_secret_key')

# Configure Gemini API client
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'AIzaSyAx0GhciWpuUyQFwO4aVKel8Tenavn-Adk')
genai.configure(api_key=GEMINI_API_KEY)


# --- Decorators ---

def login_required(f):
    """
    A decorator function that protects routes from unauthorized access.
    If 'username' is not in the session (meaning the user isn't logged in),
    they are redirected to the login page.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        # Restore user_id into session if it's missing (e.g. old session or after restart)
        if 'user_id' not in session:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT id FROM users WHERE username = %s", (session['username'],))
                row = cursor.fetchone()
                cursor.close(); conn.close()
                if row:
                    session['user_id'] = row['id']
                else:
                    session.clear()
                    return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- Routes ---

@app.route('/')
@login_required
def home():
    """Renders the main dashboard for logged-in users with real stats."""
    user_id = session.get('user_id')
    
    # Default stats
    stats = {'total_users': 0, 'total_debates': 0, 'available_topics': 50}
    recent_debates = []
    
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        # Global stats
        cursor.execute("SELECT COUNT(*) as count FROM users")
        stats['total_users'] = cursor.fetchone()['count']
        cursor.execute("SELECT COUNT(*) as count FROM debate_sessions")
        stats['total_debates'] = cursor.fetchone()['count']
        
        # User's recent debates
        if user_id:
            cursor.execute("""
                SELECT topic, started_at as date, result, id 
                FROM debate_sessions 
                WHERE user_id = %s 
                ORDER BY started_at DESC 
                LIMIT 5
            """, (user_id,))
            recent_debates = cursor.fetchall()
            
        cursor.close()
        conn.close()

    return render_template('index.html', 
                            username=session['username'],
                            stats=stats,
                            recent_debates=recent_debates)

# Login route: Handles GET (shows form) and POST (processes login) requests
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Authenticates the user and initiates a session."""
    if request.method == 'POST':
        # Sanitize inputs by stripping leading/trailing whitespace
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
            user = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if user:
                session['username'] = username  # Log the user in by storing in session
                session['user_id'] = user['id']
                return redirect(url_for('home'))
        
        # In a real app, flash a generic error message (e.g., "Invalid credentials")
        # to avoid leaking whether the username exists or the password was wrong.
        return 'Invalid credentials'
    return render_template('login.html')

# Signup route: Handles GET (shows form) and POST (creates account) requests
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Registers a new user and sets up their default profile."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not password:
            return 'Username and password cannot be empty'

        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                cursor.close()
                conn.close()
                return 'Username already exists'
                
            joined_date = date.today().strftime('%b %d, %Y')
            cursor.execute(
                "INSERT INTO users (username, password, display_name, joined_date) VALUES (%s, %s, %s, %s)",
                (username, password, username, joined_date)
            )
            conn.commit()
            
            # Fetch newly created user ID
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            user_id = cursor.fetchone()['id']
            
            # Initialize default progress
            default_skills = ['Debate Skills', 'Argument Quality', 'Critical Thinking', 'Topic Knowledge']
            for skill in default_skills:
                cursor.execute(
                    "INSERT INTO user_progress (user_id, skill_label, skill_value) VALUES (%s, %s, %s)",
                    (user_id, skill, 0)
                )
            conn.commit()
            cursor.close()
            conn.close()
            
            session['username'] = username
            session['user_id'] = user_id
            return redirect(url_for('home'))
        return 'Database connection failed'
    return render_template('signup.html')

# Features route: Shows the features page
@app.route('/features')
@login_required
def features():
    """Renders the features explanation page."""
    return render_template('features.html', username=session['username'])

@app.route('/why_platform')
@login_required
def why_platform():
    """Renders the philosophical reasoning behind the platform."""
    return render_template('why_platform.html', username=session['username'])

@app.route('/how_it_works')
@login_required
def how_it_works():
    """Renders a guide on how the AI debate logic functions."""
    return render_template('how_it_works.html', username=session['username'])

@app.route('/topics')
@login_required
def topics():
    """Renders the topic selection UI."""
    return render_template('topics.html', username=session['username'])

# Debate route: Dynamic route that takes a 'topic' parameter in the URL
@app.route('/debate/<topic>')
@login_required
def debate(topic):
    # Check if viewing a previous debate (passed as query parameter)
    view_past = request.args.get('view_past', 'false').lower() == 'true'
    user_id = session.get('user_id')
    
    # Format the topic string
    topic_display = topic.replace('_', ' ')
    conversation = []
    
    if view_past:
        conn = get_db_connection()
        if conn and user_id:
            cursor = conn.cursor(dictionary=True)
            # Find the MOST RECENT session for this topic for this user
            cursor.execute("""
                SELECT conversation_json 
                FROM debate_sessions 
                WHERE user_id = %s AND topic = %s AND conversation_json IS NOT NULL
                ORDER BY started_at DESC LIMIT 1
            """, (user_id, topic_display))
            row = cursor.fetchone()
            if row and row['conversation_json']:
                import json
                try:
                    conversation = json.loads(row['conversation_json'])
                except:
                    conversation = []
            cursor.close(); conn.close()

    # Render the debate template, passing in the topic and conversation history
    return render_template('debate.html', username=session['username'], topic=topic_display, 
                            view_past=view_past, conversation=conversation)

@app.route('/profile')
@login_required
def profile():
    """Renders the comprehensive user profile and statistics page."""
    username = session['username']
    user_id = session.get('user_id')
    
    display_name, debates, wins, losses, draws, win_rate, joined = username, 0, 0, 0, 0, '0%', ''
    progress, achievements = {}, []
    
    conn = get_db_connection()
    if conn and user_id:
        cursor = conn.cursor(dictionary=True)
        # Fetch main user row
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        if user:
            display_name = user['display_name']
            debates = user['debates']
            wins = user['wins']
            losses = user['losses']
            draws = user['draws']
            win_rate = user['win_rate']
            joined = user['joined_date']
        # Fetch skill progress
        cursor.execute("SELECT skill_label, skill_value FROM user_progress WHERE user_id = %s", (user_id,))
        progress = {row['skill_label']: row['skill_value'] for row in cursor.fetchall()}
        # Fetch achievements
        cursor.execute("SELECT title, description AS descript, icon, unlocked FROM achievements WHERE user_id = %s", (user_id,))
        achievements = cursor.fetchall()
        cursor.close()
        conn.close()
    
    return render_template('profile.html',
                            username=display_name,
                            debates=debates,
                            wins=wins,
                            losses=losses,
                            draws=draws,
                            win_rate=win_rate,
                            joined=joined,
                            progress=progress,
                            achievements=achievements,
                            raw_username=username)


# --- API Endpoints (Profile Management) ---

@app.route('/profile/data')
@login_required
def profile_data():
    """Returns profile data as JSON for dynamic front-end polling."""
    user_id = session.get('user_id')
    conn = get_db_connection()
    if not conn or not user_id:
        return jsonify({'error': 'User not found'}), 404
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    if not user:
        cursor.close(); conn.close()
        return jsonify({'error': 'User not found'}), 404
    
    cursor.execute("SELECT skill_label, skill_value FROM user_progress WHERE user_id = %s", (user_id,))
    progress = {row['skill_label']: row['skill_value'] for row in cursor.fetchall()}
    cursor.execute("SELECT title, description AS descript, icon, unlocked FROM achievements WHERE user_id = %s", (user_id,))
    achievements = cursor.fetchall()
    cursor.close(); conn.close()
    
    return jsonify({
        'display_name': user['display_name'],
        'debates': user['debates'],
        'wins': user['wins'],
        'losses': user['losses'],
        'draws': user['draws'],
        'win_rate': user['win_rate'],
        'joined': user['joined_date'],
        'progress': progress,
        'achievements': achievements
    })


@app.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    """Updates simple profile attributes like display name."""
    user_id = session.get('user_id')
    display_name = request.form.get('display_name', '').strip()
    if not display_name or not user_id:
        return jsonify({'error': 'Missing data'}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'DB error'}), 500
    
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET display_name = %s WHERE id = %s", (display_name, user_id))
    conn.commit()
    cursor.close(); conn.close()
    return jsonify({'ok': True, 'display_name': display_name})


@app.route('/profile/change_password', methods=['POST'])
@login_required
def change_password():
    """Secure endpoint for changing a user password."""
    user_id = session.get('user_id')
    old = request.form.get('old_password', '').strip()
    new = request.form.get('new_password', '').strip()
    
    if not old or not new:
        return jsonify({'error': 'Missing fields'}), 400
    
    conn = get_db_connection()
    if not conn or not user_id:
        return jsonify({'error': 'DB error'}), 500
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT password FROM users WHERE id = %s", (user_id,))
    row = cursor.fetchone()
    if not row or row['password'] != old:
        cursor.close(); conn.close()
        return jsonify({'error': 'Old password incorrect'}), 403
    
    cursor.execute("UPDATE users SET password = %s WHERE id = %s", (new, user_id))
    conn.commit()
    cursor.close(); conn.close()
    return jsonify({'ok': True})


@app.route('/profile/delete', methods=['POST'])
@login_required
def delete_account():
    """Destroys a user's account and session."""
    user_id = session.get('user_id')
    conn = get_db_connection()
    if conn and user_id:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()
        cursor.close(); conn.close()
    session.pop('username', None)
    session.pop('user_id', None)
    return jsonify({'ok': True})


@app.route('/profile/progress', methods=['POST'])
@login_required
def update_progress():
    """Updates a user's skill mastery progress bars."""
    user_id = session.get('user_id')
    data = request.get_json() or request.form
    label = data.get('label')
    value = data.get('value')
    
    if label is None or value is None:
        return jsonify({'error': 'Missing label or value'}), 400
    try:
        value = int(value)
    except Exception:
        return jsonify({'error': 'Invalid value'}), 400
    
    conn = get_db_connection()
    if not conn or not user_id:
        return jsonify({'error': 'DB error'}), 500
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "INSERT INTO user_progress (user_id, skill_label, skill_value) VALUES (%s, %s, %s) "
        "ON DUPLICATE KEY UPDATE skill_value = %s",
        (user_id, label, value, value)
    )
    conn.commit()
    cursor.execute("SELECT skill_label, skill_value FROM user_progress WHERE user_id = %s", (user_id,))
    progress = {row['skill_label']: row['skill_value'] for row in cursor.fetchall()}
    cursor.close(); conn.close()
    return jsonify({'ok': True, 'progress': progress})


@app.route('/profile/achievement/unlock', methods=['POST'])
@login_required
def unlock_achievement():
    """Posts a new achievement to the user's profile."""
    user_id = session.get('user_id')
    data = request.get_json() or request.form
    title = data.get('title')
    if not title:
        return jsonify({'error': 'Missing title'}), 400
    
    conn = get_db_connection()
    if not conn or not user_id:
        return jsonify({'error': 'DB error'}), 500
    
    desc = data.get('desc', '')
    icon = data.get('icon', '⭐')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO achievements (user_id, title, description, icon, unlocked) VALUES (%s, %s, %s, %s, TRUE) "
        "ON DUPLICATE KEY UPDATE unlocked = TRUE",
        (user_id, title, desc, icon)
    )
    conn.commit()
    cursor.close(); conn.close()
    new = {'title': title, 'desc': desc, 'icon': icon, 'unlocked': True}
    return jsonify({'ok': True, 'achievement': new})

@app.route('/conversations')
@login_required
def conversations():
    """Renders a chronological history of a user's past debates."""
    user_id = session.get('user_id')
    conversations_list = []
    
    conn = get_db_connection()
    if conn and user_id:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, topic, result, messages_count, started_at as date, ai_judgment as summary 
            FROM debate_sessions 
            WHERE user_id = %s 
            ORDER BY started_at DESC
        """, (user_id,))
        conversations_list = cursor.fetchall()
        cursor.close()
        conn.close()
        
    return render_template('conversations.html', username=session['username'], conversations=conversations_list)

# Logout route: Removes the user from the session and redirects to login
@app.route('/logout')
def logout():
    session.pop('username', None) # Remove 'username' from session dictionary
    return redirect(url_for('login'))
# --- AI Integration Routes ---

@app.route('/api/start_debate', methods=['POST'])
@login_required
def start_debate():
    """Initializes a debate session in the database."""
    user_id = session.get('user_id')
    data = request.json
    topic = data.get('topic', 'General')
    position = data.get('position', 'for')
    
    conn = get_db_connection()
    if conn and user_id:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO debate_sessions (user_id, topic, position) VALUES (%s, %s, %s)",
            (user_id, topic, position)
        )
        conn.commit()
        session['debate_session_id'] = cursor.lastrowid
        cursor.close()
        conn.close()
        return jsonify({'ok': True, 'session_id': session['debate_session_id']})
    return jsonify({'error': 'DB error'}), 500

@app.route('/api/end_debate', methods=['POST'])
@login_required
def end_debate():
    """Concludes a debate, uses AI to judge, and updates user stats."""
    user_id = session.get('user_id')
    session_id = session.get('debate_session_id')
    data = request.json
    history = data.get('history', [])
    topic = data.get('topic', 'General')
    
    if not session_id or not user_id:
        return jsonify({'error': 'No active session'}), 400

    # Formal judgement from Gemini with better instructions for fairness
    convo_text = "\n".join([f"{m['sender'].upper()}: {m['text']}" for m in history])
    judge_prompt = (
        f"You are a professional, neutral debate adjudicator. Your task is to judge a debate on the topic: '{topic}'.\n\n"
        f"CONVERSATION LOG:\n{convo_text}\n\n"
        f"CRITERIA:\n"
        f"1. Logical Consistency: Did the participant make sense?\n"
        f"2. Argument Strength: Were the points compelling?\n"
        f"3. Responsiveness: Did they actually address the other side's points?\n\n"
        f"DETERMINE WINNER:\n"
        f"- 'user': If the human out-argued the AI.\n"
        f"- 'ai': If the AI out-argued the human.\n"
        f"- 'draw': If both were equally matched or the debate was too short to decide.\n\n"
        f"Respond ONLY in JSON format:\n"
        f"{{\"winner\": \"user/ai/draw\", \"explanation\": \"A 1-2 sentence objective summary of the decision.\"}}"
    )
    
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(judge_prompt)
        import json
        judge_data = json.loads(response.text.strip().replace('```json', '').replace('```', ''))
        winner = judge_data.get('winner', 'draw')
        explanation = judge_data.get('explanation', 'Debate concluded.')
    except Exception as e:
        app.logger.error(f"Judging failed: {str(e)}")
        winner = 'draw'
        explanation = 'Debate concluded (judging unavailable).'

    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        import json
        history_json = json.dumps(history)
        
        # Update session with judgment and full history content
        cursor.execute(
            "UPDATE debate_sessions SET result = %s, ai_judgment = %s, messages_count = %s, conversation_json = %s, ended_at = NOW() WHERE id = %s",
            (winner, explanation, len(history), history_json, session_id)
        )
        
        # Update user stats
        cursor.execute("SELECT wins, losses, draws, debates FROM users WHERE id = %s", (user_id,))
        user_stats = cursor.fetchone()
        
        wins, losses, draws, total = user_stats['wins'], user_stats['losses'], user_stats['draws'], user_stats['debates'] + 1
        if winner == 'user': wins += 1
        elif winner == 'ai': losses += 1
        else: draws += 1
        
        win_rate = f"{(wins / total * 100):.1f}%" if total > 0 else "0%"
        
        cursor.execute(
            "UPDATE users SET wins = %s, losses = %s, draws = %s, debates = %s, win_rate = %s WHERE id = %s",
            (wins, losses, draws, total, win_rate, user_id)
        )

        # --- AUTOMATED PROGRESS & ACHIEVEMENTS ---
        
        # 1. Update Core Skills (Progress bars)
        skills_to_update = {
            'Debate Skills': 10 if winner == 'user' else 3,
            'Argument Quality': 8 if winner == 'user' else 4,
            'Critical Thinking': 7 if winner == 'user' else 5,
            'Topic Knowledge': 5
        }
        
        for label, bump in skills_to_update.items():
            cursor.execute(
                "INSERT INTO user_progress (user_id, skill_label, skill_value) "
                "VALUES (%s, %s, %s) "
                "ON DUPLICATE KEY UPDATE skill_value = LEAST(100, skill_value + %s)",
                (user_id, label, bump, bump)
            )
            
        # 2. Unlock Specific Achievements
        if total == 1:
            cursor.execute(
                "INSERT IGNORE INTO achievements (user_id, title, description, icon) "
                "VALUES (%s, 'Ice Breaker', 'Completed your very first debate session!', '🧊')",
                (user_id,)
            )

        if winner == 'user' and wins == 1:
            cursor.execute(
                "INSERT IGNORE INTO achievements (user_id, title, description, icon) "
                "VALUES (%s, 'First Victory', 'You won your very first debate against the AI!', '🏆')",
                (user_id,)
            )
        
        if total >= 5:
            cursor.execute(
                "INSERT IGNORE INTO achievements (user_id, title, description, icon) "
                "VALUES (%s, 'Debate Veteran', 'Participated in 5 or more debates.', '🎖️')",
                (user_id,)
            )

        conn.commit()
        cursor.close()
        conn.close()
        session.pop('debate_session_id', None)
        return jsonify({'ok': True, 'winner': winner, 'explanation': explanation})
    
    return jsonify({'error': 'DB error'}), 500


@app.route('/api/debate_response', methods=['POST'])
@login_required
def api_debate_response():
    """
    Core AI API. Takes the current debate history and user stance, 
    and requests a counter-argument from the Gemini model.
    """
    data = request.json
    topic = data.get('topic', '')
    position = data.get('position', '') # 'for' or 'against'
    history = data.get('history', [])
    
    # Validation
    if not topic or not history:
        return jsonify({'error': 'Malformed request body: topic and history required.'}), 400
    
    opposing_stance = 'AGAINST' if position == 'for' else 'FOR'
    user_stance = 'FOR' if position == 'for' else 'AGAINST'
    
    system_prompt = (
        f"You are a professional, polite AI debating the topic '{topic}'. "
        f"The user is arguing {user_stance}. You MUST take the opposing side ({opposing_stance}). "
        f"Provide a concise, compelling counter-argument under 150 words. "
        f"Do not act hostile. Respond directly to the user's latest point with logical reasoning."
    )
    
    try:
        model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=system_prompt)
        chat = model.start_chat(history=[])
        
        # Populate history to give the AI context of the full conversation
        for msg in history[:-1]:  # all but the newly sent latest message
            role = "user" if msg['sender'] == 'user' else "model"
            chat.history.append({"role": role, "parts": [msg['text']]})
            
        latest_msg = history[-1]['text'] if history else "Start the debate."
        response = chat.send_message(latest_msg)
        
        return jsonify({'reply': response.text})
        
    except Exception as e:
        # Proper error logging instead of just print
        app.logger.error(f"Error communicating with Gemini API: {str(e)}")
        # Provide a graceful fallback error instead of raw technical stacks to UI
        return jsonify({'error': 'The AI engine is currently unreachable. Please try again later.'}), 503

# Run the app in debug mode when executed directly
if __name__ == '__main__':
    app.run(debug=True)
