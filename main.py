# Import the create_app function from __init__.py
from website import create_app

# Entry point for WSGI server
app = create_app()
