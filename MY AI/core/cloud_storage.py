import cloudinary
import cloudinary.uploader
import os
from flask import current_app

def init_cloudinary(app):
    # Folosim variabilele din config-ul Flask (care pot veni din .env sau server)
    cloudinary.config(
        cloud_name = app.config.get('CLOUDINARY_CLOUD_NAME'),
        api_key = app.config.get('CLOUDINARY_API_KEY'),
        api_secret = app.config.get('CLOUDINARY_API_SECRET'),
        secure = True
    )

def upload_to_cloud(file_stream, filename, is_raw=False):
    """
    Urcă fișierul pe Cloudinary (din memorie!).
    is_raw=True pentru fișiere ZIP, False pentru imagini.
    """
    try:
        # Resource type "auto" detectează singur dacă e imagine sau altceva (raw)
        resource_type = "raw" if is_raw else "image"
        
        upload_result = cloudinary.uploader.upload(
            file_stream,
            public_id = filename.split('.')[0], # Numele fișierului pe cloud
            resource_type = resource_type,
            folder = "titanshop/products"
        )
        
        # Returnăm URL-ul securizat
        return upload_result.get('secure_url')
    except Exception as e:
        print(f"FAILED CLOUD UPLOAD: {e}")
        return None
