import sys
import os

# Add the 'cpp' directory to the Python path
# This allows 'import db' and other local imports within 'cpp' to work
# correctly when the app is imported by Vercel's serverless runtime.
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, '..')
cpp_dir = os.path.join(project_root, 'cpp')
sys.path.append(cpp_dir)

from app import app
