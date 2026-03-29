<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:1a1a2e,50:16213e,100:0f3460&height=200&section=header&text=⚔️%20AI%20Debate%20Platform&fontSize=42&fontColor=e94560&animation=fadeIn&fontAlignY=38&desc=Challenge%20your%20thinking.%20Sharpen%20your%20arguments.&descAlignY=58&descColor=a8b2d8" width="100%"/>

<br/>

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.x-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![MySQL](https://img.shields.io/badge/MySQL-8.0+-4479A1?style=for-the-badge&logo=mysql&logoColor=white)](https://mysql.com)
[![Gemini](https://img.shields.io/badge/Gemini-2.5%20Flash-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://aistudio.google.com)
[![Vercel](https://img.shields.io/badge/Vercel-Deploy-000000?style=for-the-badge&logo=vercel&logoColor=white)](https://vercel.com)

<br/>

> **Go head-to-head with Google's Gemini AI across 600+ topics.**
> Track every win, sharpen every argument, and level up your debate skills over time.

<br/>

</div>

---

## 🎯 What Is This?

**AI Debate Platform** is a full-stack web application where users engage in structured, real-time debates against Google's Gemini 2.5 Flash model. Built for thinkers who want to stress-test their ideas — it tracks your performance, rewards your growth, and levels up your argumentation skills with every session.

---

## ✨ Features

<table>
<tr>
<td width="50%">

### 🤖 Real-Time AI Debating
Powered by **Gemini 2.5 Flash** — contextual, structured, and designed to push back on weak arguments.

### 📚 600+ Topics
Across **12 categories** — never run out of things to argue about.

`Science` `Law` `AI Ethics` `Technology` `Politics` `Philosophy` `Environment` `Economics` `Health` `Culture` `Education` `Society`

</td>
<td width="50%">

### 📊 Performance Tracking
Every debate is saved. Review past arguments, study your wins, and learn from your losses.

### 📈 Skill Progression
Earn measurable growth across:
- 🧠 **Debate Skills** — overall argumentation
- 💡 **Argument Quality** — clarity and logic
- 📉 **Win Rate** — your record over time

</td>
</tr>
</table>

### 🏆 Achievements

| Badge | Milestone |
|:------|:----------|
| 🧊 **Ice Breaker** | Complete your first debate |
| 🥇 **First Victory** | Win your first debate |
| 🎖️ **Debate Veteran** | Complete 50+ debates |
| ⚡ **Sharp Mind** | Achieve a 70%+ win rate |

### 💎 Premium UI
Dark-first glassmorphism design with smooth animations and fully responsive layouts — built for focus and immersion.

---

## 🛠️ Getting Started

### Prerequisites

Before you begin, make sure you have:

- ✅ Python **3.8+**
- ✅ MySQL **8.0+**
- ✅ A [Gemini API key](https://aistudio.google.com/app/apikey) *(free tier available)*

---

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/ai-debate-platform.git
cd ai-debate-platform
```

---

### 2️⃣ Database Setup

Open **MySQL Workbench** and run:

```sql
source setup_database.sql
```

This creates the `debate_platform` database and all required tables automatically.

---

### 3️⃣ Environment Configuration

Copy the example env file and fill in your values:

```bash
cp .env.example .env
```

Your `.env` file should look like this:

```env
# ── App ──────────────────────────────────────
FLASK_SECRET_KEY=your_secret_key_here

# ── Gemini AI ────────────────────────────────
GEMINI_API_KEY=your_gemini_api_key_here

# ── Database ─────────────────────────────────
DB_HOST=localhost
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_NAME=debate_platform
DB_PORT=3306
```

> [!WARNING]
> **Never commit your `.env` file.** It contains sensitive credentials.
> Only `.env.example` (with placeholder values) should be committed to version control.

---

### 4️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 5️⃣ Run the App

```bash
python cpp/app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser and start debating. ⚔️

---

## 🌐 Deploying to Vercel

<details>
<summary><b>🔽 Click to expand deployment guide</b></summary>

<br/>

**Step 1 — Set up a cloud MySQL database**

Use a free-tier cloud MySQL provider:
- [TiDB Cloud](https://pingcap.com/products/tidb-cloud) — recommended
- [Aiven](https://aiven.io/) — solid alternative

**Step 2 — Add environment variables**

In your Vercel project dashboard, go to **Settings → Environment Variables** and add all keys from your `.env` file. Never paste your actual keys anywhere public.

**Step 3 — Enable SSL**

For cloud databases, add this to your Vercel env vars:
```env
DB_SSL_DISABLED=False
```

**Step 4 — Connect your repo**

Link your GitHub repository to Vercel. It auto-deploys on every push using the included `vercel.json`.

</details>

---

## 🧰 Tech Stack

<div align="center">

| Layer | Technology |
|:------|:-----------|
| 🐍 Backend | Python 3.8+, Flask |
| 🗄️ Database | MySQL 8.0+ |
| 🤖 AI Engine | Google Gemini 2.5 Flash |
| 🎨 Frontend | HTML5, CSS3 (Glassmorphism), Vanilla JS |
| ☁️ Deployment | Vercel |

</div>

---

## 📁 Project Structure

```
ai-debate-platform/
│
├── 📂 cpp/
│   └── app.py                  # Flask application entry point
│
├── 📄 setup_database.sql       # Database initialization script
├── 📄 requirements.txt         # Python dependencies
├── 📄 vercel.json              # Vercel deployment config
├── 📄 .env.example             # Environment variable template ✅ safe to commit
└── 📄 .gitignore               # Keeps .env and secrets out of version control
```

> **Tip:** Commit `.env.example` with placeholder values as a guide for contributors. Never commit the real `.env`.

---

## 🔒 Security Notes

- 🚫 Never hardcode API keys, passwords, or secrets in source files
- ✅ Always use environment variables for credentials
- 🔁 Rotate your `GEMINI_API_KEY` and `FLASK_SECRET_KEY` immediately if accidentally exposed
- 📁 Confirm `.env` is in `.gitignore` **before** your first `git push`

---

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:0f3460,50:16213e,100:1a1a2e&height=100&section=footer" width="100%"/>

*Built By Vinayak and a lot of counterarguments.*

</div>
