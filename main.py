from flask import Flask
from routes.home import home_route
import os
from dotenv import load_dotenv


load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

app.register_blueprint(home_route)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)