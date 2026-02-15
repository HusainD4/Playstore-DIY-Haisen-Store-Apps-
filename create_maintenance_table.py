"""
Script untuk membuat table maintenance_routes (untuk fitur maintenance dashboard)
"""
from app import app, db
from app import MaintenanceRoute

def create_maintenance_table():
    """Membuat tabel maintenance_routes"""
    with app.app_context():
        try:
            # Create all tables (akan skip jika sudah ada)
            db.create_all()
            print("✅ Table maintenance_routes berhasil dibuat!")
            
            # Initialize default routes
            from app import init_maintenance_routes
            init_maintenance_routes()
            print("✅ Default maintenance routes berhasil diinisialisasi!")
            
        except Exception as e:
            print(f"❌ Error membuat tabel: {e}")

if __name__ == '__main__':
    create_maintenance_table()
