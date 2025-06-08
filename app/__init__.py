from flask import Flask
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
BASE_API_URL = os.getenv('BASE_API_URL')

from app.routes import main, reactions

app.register_blueprint(main.bp)
app.register_blueprint(reactions.bp)