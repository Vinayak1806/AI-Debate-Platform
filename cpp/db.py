import os
import mysql.connector
from dotenv import load_dotenv

# Load .env from the same directory as this file (cpp/), 
# regardless of which directory Flask is launched from
_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(_dir, '.env'))

def get_db_connection():
    """
    Creates and returns a connection to the MySQL database.
    Requires environment variables or defaults to basic local settings.
    """
    try:
        connection = mysql.connector.connect(
            host=os.environ.get('DB_HOST', 'localhost'),
            user=os.environ.get('DB_USER', 'root'),
            password=os.environ.get('DB_PASSWORD', ''),
            database=os.environ.get('DB_NAME', 'debate_platform'),
            port=int(os.environ.get('DB_PORT', '3306'))
        )
        return connection
    except mysql.connector.Error as err:
        print(f"[DB ERROR {err.errno}]: {err.msg}")
        return None
