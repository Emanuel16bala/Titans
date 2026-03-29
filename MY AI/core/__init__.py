from flask import Flask
from flask_bcrypt import Bcrypt
from flask_session import Session
import os
from dotenv import load_dotenv

# Încărcăm variabilele de mediu din .env (opțional)
load_dotenv()

app = Flask(__name__, 
            template_folder='../templates', 
            static_folder='../static')

# Configurații Generale
app.config['SECRET_KEY'] = 'titan_shop_secret_2026'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['ADMIN_PASSWORD'] = 'TITAN_ADMIN_99'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024 # 100MB max

# Cloudinary - Cheile tale (le poți pune și în .env sau pe server!)
app.config['CLOUDINARY_CLOUD_NAME'] = os.environ.get('CLOUDINARY_CLOUD_NAME') or 'dcm23knkh'
app.config['CLOUDINARY_API_KEY'] = os.environ.get('CLOUDINARY_API_KEY') or '773994521353596'
app.config['CLOUDINARY_API_SECRET'] = os.environ.get('CLOUDINARY_API_SECRET') or 'xLgCaEX-jZxxyrfNxqIllaK7gAA'

# Inițializare Cloudinary
from core import cloud_storage
cloud_storage.init_cloudinary(app)

# Pregătire foldere minime (doar pentru sistem)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.makedirs(os.path.join(BASE_DIR, 'data'), exist_ok=True)

bcrypt = Bcrypt(app)
Session(app)

from core import routes
