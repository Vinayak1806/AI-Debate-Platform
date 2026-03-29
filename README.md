make this readme file well # AI Debate Platform
A premium AI-powered debating platform that allows users to engage in logical battles with Gemini AI on over 600+ topics.
## 🚀 Features
- **Real-time AI Debating**: Powered by Google's Gemini 2.5 Flash model.
- **Persistent History**: All debates are saved to a MySQL database, allowing you to review your past arguments.
- **User Progression**: Track your stats including Wins, Losses, and Win Rate.
- **Skill Mastery**: Increase your "Debate Skills", "Argument Quality", and more through active participation.
- **Achievements**: Unlock colorful badges (Ice Breaker, First Victory, Debate Veteran) as you reach milestones.
- **Premium UI**: Glassmorphism design with smooth animations and responsive layouts.
- **Extensive Topics**: 600+ topics across 12 categories (Science, Law, AI Ethics, etc.).
## 🛠️ Setup Instructions
### 1. Database Setup
1. Open your MySQL Workbench.
2. Run the script found in `setup_database.sql`.
3. This will create the `debate_platform` database and all necessary tables.
### 2. Environment Configuration
Create a `.env` file in the **root directory** with the following:
```env
FLASK_SECRET_KEY=your_secret_key
GEMINI_API_KEY=your_gemini_api_key
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=debate_platform
DB_PORT=3306
```
### 3. Installation
```powershell
pip install -r requirements.txt
```
### 4. Run the Application
```powershell
# From the root directory:
python cpp/app.py
```
Open `http://127.0.0.1:5000` in your browser.
## 🌐 Deployment (Vercel)
1. **Cloud Database**: Set up a free MySQL instance on [TiDB Cloud](https://pingcap.com/products/tidb-cloud) or [Aiven](https://aiven.io/).
2. **Environment Variables**: Add `FLASK_SECRET_KEY`, `GEMINI_API_KEY`, and the `DB_*` variables in the Vercel dashboard. 
3. **SSL**: For cloud databases, set `DB_SSL_DISABLED=False`.
4. **Connect**: Link your GitHub repo to Vercel and it will auto-deploy using `vercel.json`.
## 🧰 Tech Stack
- **Backend**: Python, Flask, MySQL
- **AI**: Google Generative AI (Gemini)
- **Frontend**: HTML5, Vanilla CSS3 (Glassmorphism), JavaScript
