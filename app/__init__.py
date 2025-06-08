import redis
from flask import Flask
from dotenv import load_dotenv

import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
BASE_API_URL = os.getenv('BASE_API_URL')


redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
redis_conn = redis.Redis.from_url(redis_url, decode_responses=True)
CACHE_EXPIRE_SECONDS = int(os.getenv('CACHE_EXPIRE_SECONDS', 3600))


from app.routes import main, reactions

app.register_blueprint(main.bp)
app.register_blueprint(reactions.bp)