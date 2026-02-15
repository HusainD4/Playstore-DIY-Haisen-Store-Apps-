"""
Script untuk membuat database jika belum ada
"""
import pymysql

# Konfigurasi MySQL
MYSQL_HOST = 'localhost'
MYSQL_PORT = 3307
MYSQL_USER = 'root'
MYSQL_PASSWORD = ''  # Kosongkan jika tidak ada password
DATABASE_NAME = 'haisen_db'

def create_database():
    """Membuat database jika belum ada"""
    try:
        # Connect ke MySQL tanpa database
        connection = pymysql.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD
        )
        
        with connection.cursor() as cursor:
            # Buat database jika belum ada
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DATABASE_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print(f"Database '{DATABASE_NAME}' berhasil dibuat atau sudah ada!")
        
        connection.close()
        print("Setup database selesai!")
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == '__main__':
    create_database()
