import json
import os
from core import bcrypt, app

USERS_FILE = 'data/users.json'

def load_users():
    if not os.path.exists(USERS_FILE):
        return []
    with open(USERS_FILE, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except:
            return []

def save_users(users):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=2)

def register_user(username, password, role='client', secret_admin_pass=None):
    users = load_users()
    if any(u['username'] == username for u in users):
        return False, "Username already exists."
    
    if role == 'admin':
        if secret_admin_pass != app.config['ADMIN_PASSWORD']:
            return False, "Invalid admin secret password."
        
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = {
        "username": username,
        "password": hashed_password,
        "role": role
    }
    users.append(new_user)
    save_users(users)
    return True, "Registered successfully."

def login_user(username, password):
    users = load_users()
    user = next((u for u in users if u['username'] == username), None)
    if user and bcrypt.check_password_hash(user['password'], password):
        return user
    return None
