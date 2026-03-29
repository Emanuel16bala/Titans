from flask import render_template, request, redirect, url_for, session, jsonify, flash, Response
from core import app, bcrypt, store, cloud_storage
import os, requests as http_requests
from datetime import datetime

@app.context_processor
def inject_user():
    return {'session': session}

@app.route('/')
def index():
    products = store.get_products()
    content = store.get_content()
    reviews = store.get_reviews()
    return render_template('index.html', products=products, content=content, reviews=reviews)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = store.get_user(username)
        if user and bcrypt.check_password_hash(user['password'], password):
            session['user'] = user['username']
            session['role'] = user['role']
            session['grade'] = user.get('grade', 0)
            return redirect(url_for('index'))
        return render_template('login.html', error="Date incorecte!")
    return render_template('login.html')

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    role = request.form.get('role', 'client')
    secret = request.form.get('secret_admin_pass')
    
    final_role = 'client'
    final_grade = 0
    if role == 'admin' and secret == "TITAN_ROOT_2026":
        final_role = 'admin'
        final_grade = 1

    hashed = bcrypt.generate_password_hash(password).decode('utf-8')
    if store.add_user(username, hashed, final_role):
        store.update_user_info(username, grade=final_grade)
        flash("Cont creat! Loghează-te.")
        return redirect(url_for('login'))
    return render_template('login.html', error="Utilizator existent!")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/admin')
def admin_panel():
    if session.get('role') != 'admin':
        return redirect(url_for('index'))
    orders = store.get_all_orders()
    users = store.get_all_users()
    return render_template('admin.html', 
        products=store.get_products(),
        users=users if session.get('grade') >= 3 else [],
        messages=store.get_messages() if session.get('grade') >= 2 else [],
        orders_all=orders if session.get('grade') >= 2 else [],
        content=store.get_content(),
        reviews=store.get_reviews(),
        total_sales=sum([o['total'] for o in orders]),
        order_count=len(orders),
        admin_count=len([u for u in users if u['role'] == 'admin']),
        client_count=len([u for u in users if u['role'] == 'client']))

@app.route('/admin/add', methods=['POST'])
def admin_add_product():
    if session.get('grade', 0) < 2: return redirect(url_for('index'))
    n, p, c, d = request.form['name'], request.form['price'], request.form['category'], request.form['description']
    img, zipf = request.files.get('image_file'), request.files.get('zip_file')
    img_u = cloud_storage.upload_to_cloud(img, img.filename, False) if img else ""
    zip_u = cloud_storage.upload_to_cloud(zipf, zipf.filename, True) if zipf else ""
    store.add_product(n, p, c, img_u, zip_u, d, zip_u)
    return redirect(url_for('admin_panel'))

@app.route('/admin/edit/<int:pid>', methods=['POST'])
def admin_edit_product(pid):
    if session.get('grade', 0) < 2: return redirect(url_for('index'))
    n, p, c, d = request.form['name'], request.form['price'], request.form['category'], request.form['description']
    img, zipf = request.files.get('image_file'), request.files.get('zip_file')
    img_u = cloud_storage.upload_to_cloud(img, img.filename, False) if img and img.filename else ""
    zip_u = cloud_storage.upload_to_cloud(zipf, zipf.filename, True) if zipf and zipf.filename else ""
    store.update_product_full(pid, n, p, c, img_u, zip_u, d, zip_u)
    return redirect(url_for('admin_panel'))

@app.route('/admin/delete/<int:pid>')
def admin_delete_product(pid):
    if session.get('grade', 0) < 2: return redirect(url_for('index'))
    store.delete_product(pid)
    return redirect(url_for('admin_panel'))

@app.route('/admin/orders/delete/<oid>')
def admin_order_delete(oid):
    if session.get('grade', 0) < 2: return redirect(url_for('index'))
    store.delete_order(oid)
    return redirect(url_for('admin_panel'))

@app.route('/admin/users/update', methods=['POST'])
def admin_user_update():
    if session.get('grade', 0) < 3: return redirect(url_for('index'))
    target = request.form.get('target_username')
    new_e, new_r, new_g, new_p = request.form.get('email'), request.form.get('role'), request.form.get('grade'), request.form.get('password')
    h = bcrypt.generate_password_hash(new_p).decode('utf-8') if new_p else None
    store.admin_update_user(target, target, new_e, h, new_r, new_g)
    return redirect(url_for('admin_panel'))

@app.route('/admin/content/update', methods=['POST'])
def admin_content_update():
    if session.get('grade', 0) < 3: return jsonify(success=False)
    store.update_content({
        "hero_title": request.form.get('hero_title'),
        "hero_subtitle": request.form.get('hero_subtitle'),
        "terms": request.form.get('terms'),
        "privacy": request.form.get('privacy'),
        "faq": store.get_content().get('faq', [])
    })
    flash("S-a salvat conținutul!")
    return redirect(url_for('admin_panel'))

@app.route('/support/contact', methods=['POST'])
def support_contact():
    sub_orig, msg_orig, e = request.form.get('subject', ''), request.form.get('message', ''), request.form.get('email')
    s, m = sub_orig.lower(), msg_orig.lower()
    bad = ['prost', 'tampit', 'muie', 'pula', 'fmm', 'bag']
    if any(w in s or w in m for w in bad): flash("Limbaj interzis!")
    else: store.add_message(session.get('user', 'Guest'), e, sub_orig, msg_orig); flash("Mesaj trimis cu succes către Support!")
    return redirect(url_for('support'))

@app.route('/checkout', methods=['POST'])
def checkout():
    if 'user' not in session: return jsonify(success=False)
    data = request.get_json()
    import uuid
    oid = str(uuid.uuid4())[:8]
    orders = store.load_data(store.ORDERS_FILE)
    
    # Enrich cart items with drive_url and zip from product catalog
    products_catalog = {str(p['id']): p for p in store.get_products()}
    enriched_items = []
    for item in data.get('items', []):
        pid = str(item.get('id', ''))
        catalog_product = products_catalog.get(pid, {})
        enriched_item = {
            **item,
            'drive_url': catalog_product.get('drive_url', item.get('drive_url', '')),
            'zip': catalog_product.get('zip', item.get('zip', '')),
            'image': catalog_product.get('image', item.get('image', '')),
        }
        enriched_items.append(enriched_item)
    
    new_order = {
        "id": oid,
        "user": session['user'],
        "total": data['total'],
        "products": enriched_items,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    orders.append(new_order)
    store.save_data(store.ORDERS_FILE, orders)
    return jsonify(success=True)

@app.route('/submit_review', methods=['POST'])
def submit_review():
    if 'user' not in session: return jsonify(success=False)
    store.add_review(session['user'], request.form.get('comment'), request.form.get('rating'), request.form.get('product_id'))
    return jsonify(success=True)

@app.route('/secure-download')
def secure_download():
    """Proxy route that fetches a file from Cloudinary and serves it as a proper ZIP download."""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    file_url = request.args.get('url', '')
    filename = request.args.get('name', 'download') + '.zip'
    
    if not file_url or 'cloudinary.com' not in file_url:
        return "URL invalid sau acces refuzat.", 403
    
    try:
        # Fetch file from Cloudinary server-side
        r = http_requests.get(file_url, stream=True, timeout=30)
        r.raise_for_status()
        
        def generate():
            for chunk in r.iter_content(chunk_size=8192):
                yield chunk
        
        return Response(
            generate(),
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"',
                'Content-Type': 'application/zip',
                'Content-Length': r.headers.get('Content-Length', '')
            }
        )
    except Exception as e:
        return f"Eroare la descarcare: {str(e)}", 500

@app.route('/orders')
def orders():
    if 'user' not in session: return redirect(url_for('login'))
    user_orders = store.get_user_orders(session['user'])
    return render_template('orders.html', orders=user_orders)

@app.route('/profile')
def profile():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('profile.html', user=store.get_user(session['user']))

@app.route('/support')
def support(): return render_template('support.html')

@app.route('/terms')
def terms(): return render_template('legal.html', content=store.get_content())
@app.route('/privacy')
def privacy(): return render_template('legal.html', content=store.get_content())
@app.route('/cart')
def cart(): return render_template('cart.html')
