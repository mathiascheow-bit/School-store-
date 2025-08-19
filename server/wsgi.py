import sys
import os

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Import the app
from app import app as application

# WSGI callable
if __name__ == "__main__":
    application.run()
