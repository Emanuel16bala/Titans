import json
import os
from datetime import datetime

PRODUCTS_FILE = 'data/products.json'
ORDERS_FILE = 'data/orders.json'
REVIEWS_FILE = 'data/reviews.json'
MESSAGES_FILE = 'data/contact.json'
CONTENT_FILE = 'data/content.json'

def load_data(file_name):
    if not os.path.exists(file_name):
        return []
    with open(file_name, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except:
            return []

def save_data(file_name, data):
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def get_user(username):
    users = load_data('data/users.json')
    return next((u for u in users if u['username'] == username), None)

def add_user(username, password, role='client'):
    users = load_data('data/users.json')
    if any(u['username'] == username for u in users): return False
    users.append({"username": username, "password": password, "role": role, "grade": 0})
    save_data('data/users.json', users)
    return True

def get_products():
    return load_data(PRODUCTS_FILE)

def add_product(name, price, category, image_url, zip_file_name, description, drive_url=""):
    products = get_products()
    new_id = max([p['id'] for p in products]) + 1 if products else 1
    new_product = {
        "id": new_id,
        "name": name,
        "price": float(price),
        "category": category,
        "image": image_url,
        "zip": zip_file_name,
        "description": description,
        "drive_url": drive_url
    }
    products.append(new_product)
    save_data(PRODUCTS_FILE, products)
    return new_product

def delete_product(product_id):
    products = get_products()
    products = [p for p in products if p['id'] != int(product_id)]
    save_data(PRODUCTS_FILE, products)

def update_product_full(product_id, name, price, category, image, zip_file, description, drive_url=""):
    products = get_products()
    for p in products:
        if p['id'] == int(product_id):
            if name: p['name'] = name
            if price: p['price'] = float(price)
            if category: p['category'] = category
            if image: p['image'] = image
            if zip_file: p['zip'] = zip_file
            if description: p['description'] = description
            if drive_url: p['drive_url'] = drive_url
            break
    save_data(PRODUCTS_FILE, products)

def create_order(username, cart_items, total, email=""):
    orders = load_data(ORDERS_FILE)
    new_order = {
        "user": username,
        "email": email,
        "products": cart_items,
        "total": float(total),
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    orders.append(new_order)
    save_data(ORDERS_FILE, orders)
    return True

def get_user_orders(username):
    orders = load_data(ORDERS_FILE)
    return [o for o in orders if o['user'] == username]

def get_all_orders():
    return load_data(ORDERS_FILE)

def delete_order(mid):
    orders = load_data(ORDERS_FILE)
    # Using enumerate or index to find and delete
    orders = [o for o in orders if o.get('id') != mid]
    save_data(ORDERS_FILE, orders)

def update_user_info(username, email=None, new_password=None, grade=None):
    users = load_data('data/users.json')
    for u in users:
        if u['username'] == username:
            if email: u['email'] = email
            if new_password: u['password'] = new_password
            if grade is not None: u['grade'] = int(grade)
            save_data('data/users.json', users)
            return True
    return False

def get_all_users():
    return load_data('data/users.json')

def admin_update_user(target_username, new_user, new_email, new_pass, new_role, new_grade):
    users = load_data('data/users.json')
    for u in users:
        if u['username'] == target_username:
            u['username'] = new_user
            u['email'] = new_email
            if new_pass: u['password'] = new_pass
            u['role'] = new_role
            u['grade'] = int(new_grade)
            save_data('data/users.json', users)
            return True
    return False

# --- SUPPORT MESSAGES ---
def add_message(username, email, subject, content):
    msgs = load_data(MESSAGES_FILE)
    msgs.append({
        "id": len(msgs) + 1,
        "user": username,
        "email": email,
        "subject": subject,
        "content": content,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "pending"
    })
    save_data(MESSAGES_FILE, msgs)

def get_messages():
    return load_data(MESSAGES_FILE)

def delete_message(mid):
    msgs = load_data(MESSAGES_FILE)
    msgs = [m for m in msgs if m['id'] != int(mid)]
    save_data(MESSAGES_FILE, msgs)

# --- DYNAMIC CONTENT & REVIEWS ---
def get_content():
    if not os.path.exists(CONTENT_FILE):
        return {
            "hero_title": "Tech-Focused Marketplace",
            "hero_subtitle": "Descoperă cele mai avansate resurse digitale, scripturi și software premium pentru proiectele tale de viitor.",
            "terms": "Termeni Standard...",
            "privacy": "Privacy Standard...",
            "faq": []
        }
    return load_data(CONTENT_FILE)

def update_content(new_data):
    save_data(CONTENT_FILE, new_data)

def get_reviews():
    return load_data(REVIEWS_FILE)

def add_review(username, comment, rating=5, product_id=None):
    revs = load_data(REVIEWS_FILE)
    revs.append({
        "user": username, 
        "comment": comment, 
        "rating": int(rating), 
        "product_id": str(product_id),
        "date": datetime.now().strftime("%Y-%m-%d")
    })
    save_data(REVIEWS_FILE, revs)

def delete_review(idx):
    revs = load_data(REVIEWS_FILE)
    if 0 <= int(idx) < len(revs):
        revs.pop(int(idx))
        save_data(REVIEWS_FILE, revs)
