import sys
import subprocess
import os

def install_dependencies():
    """Instalează direct bibliotecile necesare din cod fără a căuta fișiere externe"""
    try:
        import flask
        # Dacă flask este prezent, mediul este gata
    except ImportError:
        print("🔧 Găsit biblioteci offline. Se începe instalarea automată directă...")
        try:
            # Lista directă de biblioteci necesare pentru Titan Shop
            libs = [
                "flask", 
                "python-dotenv", 
                "flask-bcrypt", 
                "flask-session", 
                "cloudinary",
                "gunicorn"
            ]
            # Instalăm folosind sys.executable pentru a asigura folosirea aceleiași versiuni de Python
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + libs)
            print("✅ Toate bibliotecile au fost instalate! Site-ul pornește...")
        except Exception as e:
            print(f"❌ Eroare gravă la configurare: {e}")
            sys.exit(1)

# Pornim auto-instalatorul înainte de orice alt import
install_dependencies()

# Acum site-ul poate importa corect totul
from core import app

if __name__ == '__main__':
    # Railway/Render oferă portul prin variabila PORT
    port = int(os.environ.get('PORT', 5000))
    # Site-ul este acum accesibil pe adresa publică 0.0.0.0
    app.run(host='0.0.0.0', port=port)
