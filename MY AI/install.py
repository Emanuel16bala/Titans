import os
import subprocess
import sys

def run_command(command):
    print(f"Executing: {command}")
    try:
        subprocess.check_call(command, shell=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        return False

def setup():
    print("--- 💠 Titan Shop: Auto-Installer 💠 ---")
    
    # 1. Check if requirements.txt exists
    if not os.path.exists("requirements.txt"):
        print("Error: requirements.txt not found!")
        return

    # 2. Install dependencies
    print("\n[1/3] Installing dependencies...")
    if run_command(f"{sys.executable} -m pip install -r requirements.txt"):
        print("Dependencies installed successfully.")
    else:
        print("Failed to install dependencies.")
        return

    # 3. Create data directory and empty JSONs if they don't exist
    print("\n[2/3] Checking data integrity...")
    data_dir = "data"
    files = ["users.json", "products.json", "orders.json"]
    
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"Created directory: {data_dir}")

    for file in files:
        path = os.path.join(data_dir, file)
        if not os.path.exists(path):
            with open(path, "w") as f:
                f.write("[]" if file != "products.json" else "[]")
            print(f"Created empty data file: {path}")

    # 4. Success
    print("\n[3/3] Installation complete!")
    print("\nTo start Titan Shop, run: python main.py")
    
    start_now = input("\nDo you want to start the server now? (y/n): ").lower()
    if start_now == 'y':
        run_command(f"{sys.executable} main.py")

if __name__ == "__main__":
    setup()
