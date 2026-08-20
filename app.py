from flask import Flask
from dotenv import load_dotenv
import os

load_dotenv()

from config.database import init_db, db

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

init_db(app)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)
