"""
Script untuk membuat tabel-tabel baru untuk history dan follow features
"""
from app import app, db
from app import AppUpload, AppDownload, UserFollowDeveloper, Notification

def create_new_tables():
    """Membuat tabel baru untuk history dan notifications"""
    with app.app_context():
        try:
            # Create all new tables
            db.create_all()
            print("✅ Semua tabel berhasil dibuat!")
            print("   - app_uploads")
            print("   - app_downloads")
            print("   - user_follow_developer")
            print("   - notifications")
        except Exception as e:
            print(f"❌ Error membuat tabel: {e}")

if __name__ == '__main__':
    create_new_tables()
