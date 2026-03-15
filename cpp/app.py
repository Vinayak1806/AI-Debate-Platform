from flask import Flask, render_template, request, redirect, url_for, session
import google.generativeai as genai

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a random secret key

# Configure Gemini
genai.configure(api_key='AIzaSyAx0GhciWpuUyQFwO4aVKel8Tenavn-Adk')

# Simple in-memory user storage (for demo purposes)
users = {}

# --- Routes ---

# Home route: Redirects to login if not authenticated, otherwise shows the home page
@app.route('/')
def home():
    if 'username' in session:
        return render_template('index.html', username=session['username'])
    return redirect(url_for('login'))

# Login route: Handles GET (shows form) and POST (processes login) requests
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Simple username/password check against our in-memory dictionary
        if username in users and users[username] == password:
            session['username'] = username  # Log the user in by storing in session
            return redirect(url_for('home'))
        return 'Invalid credentials'
    return render_template('login.html')

# Signup route: Handles GET (shows form) and POST (creates account) requests
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Simple check to ensure username doesn't already exist
        if username not in users:
            users[username] = password      # Save the new user
            session['username'] = username  # Automatically log the new user in
            return redirect(url_for('home'))
        return 'Username already exists'
    return render_template('signup.html')

# Features route: Shows the features page, requires login
@app.route('/features')
def features():
    if 'username' in session:
        return render_template('features.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/why_platform')
def why_platform():
    if 'username' in session:
        return render_template('why_platform.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/how_it_works')
def how_it_works():
    if 'username' in session:
        return render_template('how_it_works.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/topics')
def topics():
    if 'username' in session:
        return render_template('topics.html', username=session['username'])
    return redirect(url_for('login'))

# Debate route: Dynamic route that takes a 'topic' parameter in the URL
@app.route('/debate/<topic>')
def debate(topic):
    if 'username' in session:
        # Check if viewing a previous debate (passed as query parameter)
        view_past = request.args.get('view_past', 'false').lower() == 'true'
        
        # Sample past conversation data (in real app, this would come from database)
        past_conversations = {
            'AI_Ethics': [
                {'sender': 'user', 'text': 'AI has brought tremendous benefits to society, from healthcare advancements to solving complex problems.', 'time': '2:30 PM'},
                {'sender': 'ai', 'text': 'While AI offers benefits, we must consider the ethical implications of creating systems that can make autonomous decisions affecting human lives.', 'time': '2:31 PM'},
                {'sender': 'user', 'text': 'The key is proper oversight and regulation, not banning AI development entirely.', 'time': '2:33 PM'},
                {'sender': 'ai', 'text': 'The key concern is accountability - who is responsible when an AI system makes a harmful decision? We need clear frameworks.', 'time': '2:35 PM'},
                {'sender': 'user', 'text': 'Agreed. I believe we need international guidelines similar to nuclear non-proliferation treaties.', 'time': '2:37 PM'},
                {'sender': 'ai', 'text': 'An interesting perspective. However, AI technology evolves much faster than international agreements can be negotiated.', 'time': '2:39 PM'},
            ],
            'Climate_Change': [
                {'sender': 'user', 'text': 'Climate change is primarily caused by human activities and requires immediate action.', 'time': '4:15 PM'},
                {'sender': 'ai', 'text': 'While human contribution is significant, we should consider natural climate cycles as well.', 'time': '4:17 PM'},
                {'sender': 'user', 'text': 'The scientific consensus is clear - anthropogenic CO2 emissions are the main driver.', 'time': '4:19 PM'},
                {'sender': 'ai', 'text': 'Individual actions are important, but systemic changes in industry and agriculture are crucial for meaningful impact.', 'time': '4:21 PM'},
            ],
            'Education_Reform': [
                {'sender': 'user', 'text': 'Our education system needs to focus more on critical thinking rather than memorization.', 'time': '10:00 AM'},
                {'sender': 'ai', 'text': 'Traditional education models were designed for industrial age needs. We need to adapt to the information age.', 'time': '10:02 AM'},
                {'sender': 'user', 'text': 'Exactly! Standardized testing has limitations in measuring real-world skills.', 'time': '10:04 AM'},
                {'sender': 'ai', 'text': 'Personalized learning enabled by technology could address individual student needs more effectively.', 'time': '10:06 AM'},
            ],
            'Universal_Basic_Income': [
                {'sender': 'user', 'text': 'UBI could provide a safety net in an increasingly automated economy.', 'time': '3:30 PM'},
                {'sender': 'ai', 'text': 'Funding such a program at scale is challenging. Where would the money come from?', 'time': '3:32 PM'},
                {'sender': 'user', 'text': 'Automation companies should contribute through taxes on their profits.', 'time': '3:34 PM'},
                {'sender': 'ai', 'text': "There's concern that UBI might reduce work incentives, though evidence from pilot programs suggests otherwise.", 'time': '3:36 PM'},
            ],
            'Social_Media_Regulation': [
                {'sender': 'user', 'text': 'Social media companies should be held accountable for misinformation on their platforms.', 'time': '11:00 AM'},
                {'sender': 'ai', 'text': 'Free speech is a fundamental right. Who decides what is misinformation?', 'time': '11:02 AM'},
                {'sender': 'user', 'text': 'Independent fact-checking organizations could help verify information.', 'time': '11:04 AM'},
                {'sender': 'ai', 'text': 'The line between opinion and fact can be blurry. Regulation needs to be carefully crafted.', 'time': '11:06 AM'},
            ]
        }
        
        # Format the topic string to lookup in our sample dictionary
        topic_key = topic.replace(' ', '_')
        conversation = past_conversations.get(topic_key, [])
        
        # Render the debate template, passing in the topic and conversation history
        return render_template('debate.html', username=session['username'], topic=topic.replace('_', ' '), 
                             view_past=view_past, conversation=conversation)
    return redirect(url_for('login'))

@app.route('/profile')
def profile():
    if 'username' in session:
        return render_template('profile.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/conversations')
def conversations():
    if 'username' in session:
        # Sample conversations data (in real app, this would come from database)
        conversations_list = [
            {
                'id': 1,
                'topic': 'AI Ethics',
                'date': '2026-03-15',
                'participants': ['User1', 'User2'],
                'summary': 'Discussed the moral implications of AI decision-making in healthcare...'
            },
            {
                'id': 2,
                'topic': 'Climate Change Policy',
                'date': '2026-03-12',
                'participants': ['User3', 'User4'],
                'summary': 'Debated on government intervention vs individual responsibility...'
            },
            {
                'id': 3,
                'topic': 'Education Reform',
                'date': '2026-03-08',
                'participants': ['User5', 'User6'],
                'summary': 'Explored the pros and cons of standardized testing...'
            },
            {
                'id': 4,
                'topic': 'Universal Basic Income',
                'date': '2026-03-05',
                'participants': ['User7', 'User8'],
                'summary': 'Discussed economic impacts and feasibility of UBI...'
            },
            {
                'id': 5,
                'topic': 'Social Media Regulation',
                'date': '2026-03-01',
                'participants': ['User9', 'User10'],
                'summary': 'Debated free speech vs content moderation...'
            }
        ]
        return render_template('conversations.html', username=session['username'], conversations=conversations_list)
    return redirect(url_for('login'))

# Logout route: Removes the user from the session and redirects to login
@app.route('/logout')
def logout():
    session.pop('username', None) # Remove 'username' from session dictionary
    return redirect(url_for('login'))

@app.route('/api/debate_response', methods=['POST'])
def api_debate_response():
    if 'username' not in session:
        return {'error': 'Unauthorized'}, 401
    
    data = request.json
    topic = data.get('topic', '')
    position = data.get('position', '') # 'for' or 'against'
    history = data.get('history', [])
    
    opposing_stance = 'AGAINST' if position == 'for' else 'FOR'
    user_stance = 'FOR' if position == 'for' else 'AGAINST'
    
    system_prompt = f"You are an AI debating the topic '{topic}'. The user is arguing {user_stance}. You must take the opposing side ({opposing_stance}). Provide concise, compelling counter-arguments. Keep your responses under 100 words. Respond directly to the user's latest point."
    
    try:
        model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=system_prompt)
        chat = model.start_chat(history=[])
        
        # Populate history
        for msg in history[:-1]:  # all but the latest
            role = "user" if msg['sender'] == 'user' else "model"
            chat.history.append({"role": role, "parts": [msg['text']]})
            
        latest_msg = history[-1]['text'] if history else ""
        response = chat.send_message(latest_msg)
        
        return {'reply': response.text}
    except Exception as e:
        print(f"Error from Gemini API: {e}")
        return {'error': str(e)}, 500

# Run the app in debug mode when executed directly
if __name__ == '__main__':
    app.run(debug=True)