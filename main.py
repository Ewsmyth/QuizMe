# Import the create_app function from __init__.py
from website import create_app

# Assigns the variable app to the function create_app
app = create_app()

if __name__ == "__main__":
    # Initilizes the Flask Server
    app.run(debug=True, host="0.0.0.0", port=6678)