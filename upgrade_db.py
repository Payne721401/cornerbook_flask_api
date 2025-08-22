from flask import current_app
from flask_migrate import upgrade
from app import create_app
import os

# 設置環境變數，以確保 Flask 能夠找到應用程式
os.environ['FLASK_APP'] = 'app.py'

# 創建 Flask 應用實例
app = create_app()

with app.app_context():
    print("Starting database migration...")
    try:
        upgrade()
        print("Database migration completed successfully.")
    except Exception as e:
        print(f"An error occurred during migration: {e}")
        raise
    