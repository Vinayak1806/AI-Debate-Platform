import os
import mysql.connector
from dotenv import load_dotenv

# Load .env from the current directory
_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(_dir, '.env'))

def migrate():
    try:
        conn = mysql.connector.connect(
            host=os.environ.get('DB_HOST', 'localhost'),
            user=os.environ.get('DB_USER', 'root'),
            password=os.environ.get('DB_PASSWORD', ''),
            database=os.environ.get('DB_NAME', 'debate_platform'),
            port=int(os.environ.get('DB_PORT', '3306'))
        )
        cursor = conn.cursor()

        # Update users table with new stats columns if they don't exist
        print("Checking users table columns...")
        cursor.execute("SHOW COLUMNS FROM users")
        columns = [column[0] for column in cursor.fetchall()]
        
        new_columns = [
            ("wins", "INT DEFAULT 0"),
            ("losses", "INT DEFAULT 0"),
            ("draws", "INT DEFAULT 0")
        ]
        
        for col_name, col_type in new_columns:
            if col_name not in columns:
                print(f"Adding column {col_name} to users table...")
                cursor.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")
        
        # Create debate_sessions table if it doesn't exist
        print("Creating debate_sessions table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS debate_sessions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                topic VARCHAR(255) NOT NULL,
                position VARCHAR(10) NOT NULL,
                result VARCHAR(10) DEFAULT NULL,
                messages_count INT DEFAULT 0,
                ai_judgment TEXT DEFAULT NULL,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ended_at TIMESTAMP NULL DEFAULT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        conn.commit()
        cursor.close()
        conn.close()
        print("Migration successful!")
    except Exception as e:
        print(f"Migration failed: {e}")

if __name__ == "__main__":
    migrate()
