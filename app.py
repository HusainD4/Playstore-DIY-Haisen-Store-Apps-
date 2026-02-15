"""
Aplikasi Flask - UI Seperti Play Store dan Google Drive
Dengan sistem login Admin dan User
Database: XAMPP MySQL port 3307
"""

import os
import re
import shutil
import uuid
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, render_template, redirect, url_for, request, flash, send_from_directory, current_app, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
from sqlalchemy import func

# ==================== EMAIL CONFIGURATION ====================
# Email configuration for sending notifications
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_EMAIL = "haisen.bussines@gmail.com"
SMTP_PASSWORD = "uqql ytse deno bfcj" 

def send_email(to_email, subject, body):
    """Send email to user"""
    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def send_developer_approval_email(user, raw_password):
    """Send approval notification to developer"""
    subject = "Selamat! Pendaftaran Developer Anda Disetujui - Haisen Official"
    
    body = f"""
    Halo {user.username},

    Selamat! Pendaftaran Anda sebagai Developer di Haisen Official telah DISETUJUI.

    Berikut adalah informasi akun Anda:
    ─────────────────────────────────────
    Username: {user.username}
    Email: {user.email}
    Password: {raw_password}
    ─────────────────────────────────────

    Anda sekarang dapat:
    ✓ Login ke akun developer Anda
    ✓ Mengupload aplikasi ke platform Haisen Official
    ✓ Mengelola aplikasi yang Anda publikasikan

    Silakan login melalui link berikut:
    {url_for('login', _external=True)}

    Jika Anda memiliki pertanyaan, jangan hesitate untuk menghubungi kami.

    Best regards,
    Tim Haisen Official
    """
    
    return send_email(user.email, subject, body)

def send_account_deletion_approved_email(user):
    """Send account deletion approval notification"""
    subject = "Permohonan Penghapusan Akun Anda Telah Disetujui - Haisen Official"
    
    body = f"""
    Halo {user.username},

    Kami telah memproses permohonan penghapusan akun Anda.

    📋 DETAIL PENGHAPUSAN AKUN:
    ─────────────────────────────────────
    Username: {user.username}
    Email: {user.email}
    Tanggal Penghapusan: {datetime.utcnow().strftime('%d %B %Y')}
    Status: ✅ DISETUJUI
    ─────────────────────────────────────

    Semua data akun Anda telah dihapus dari sistem kami secara permanen, termasuk:
    ✓ Profil pengguna
    ✓ Riwayat login
    ✓ Data transaksi dan unduhan
    ✓ Review dan rating Anda

    Terima kasih telah menggunakan Haisen Official. Jika Anda ingin mendaftar kembali di masa depan, silakan kunjungi:
    {url_for('register', _external=True)}

    Kami berharap dapat melayani Anda lagi di kemudian hari.

    Salam hangat,
    Tim Haisen Official
    """
    
    return send_email(user.email, subject, body)

def send_account_deletion_rejected_email(user):
    """Send account deletion rejection notification"""
    subject = "Update: Permohonan Penghapusan Akun Anda - Haisen Official"
    
    body = f"""
    Halo {user.username},

    Terima kasih telah menghubungi kami mengenai permohonan penghapusan akun.

    ❌ KEPUTUSAN: Permohonan Anda Ditolak
    ─────────────────────────────────────

    Permohonan penghapusan akun Anda telah ditinjau dan tidak dapat diproses pada saat ini. 

    Alasan yang mungkin:
    • Akun masih memiliki aplikasi yang aktif (untuk developer)
    • Proses verifikasi belum selesai
    • Masalah keamanan akun

    Jika Anda memiliki pertanyaan atau ingin mendiskusikan lebih lanjut, silakan hubungi tim support kami di:
    📧 Email: haisen.bussines@gmail.com

    Akun Anda tetap aktif dan dapat digunakan secara normal.

    Terima kasih,
    Tim Haisen Official
    """
    
    return send_email(user.email, subject, body)

def send_help_request_response_email(help_request):
    """Send email notification to user when admin responds to their help request"""
    
    # Status mapping with colors
    status_info = {
        'pending': {'text': 'Menunggu', 'color': '#f59e0b', 'bg': '#fef3c7'},
        'in_progress': {'text': 'Sedang Diproses', 'color': '#3b82f6', 'bg': '#dbeafe'},
        'resolved': {'text': 'Selesai', 'color': '#10b981', 'bg': '#d1fae5'},
        'closed': {'text': 'Ditutup', 'color': '#6b7280', 'bg': '#f3f4f6'}
    }
    
    status = status_info.get(help_request.status, {'text': help_request.status, 'color': '#6b7280', 'bg': '#f3f4f6'})
    
    subject = f"Update Permintaan Bantuan Anda - {help_request.issue_description} - Haisen Official"
    
    # HTML Email Template with boxes
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{subject}</title>
    </head>
    <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f3f4f6; color: #1f2937;">
        <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f3f4f6; padding: 20px;">
            <tr>
                <td align="center">
                    <table width="100%" cellpadding="0" cellspacing="0" style="max-width: 600px; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
                        <!-- Header -->
                        <tr>
                            <td style="background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%); padding: 30px; text-align: center;">
                                <h1 style="margin: 0; color: #ffffff; font-size: 24px; font-weight: 600;">Haisen Official</h1>
                                <p style="margin: 5px 0 0 0; color: #e0e7ff; font-size: 14px;">Pusat Bantuan & Dukungan</p>
                            </td>
                        </tr>
                        
                        <!-- Greeting -->
                        <tr>
                            <td style="padding: 30px 30px 20px 30px;">
                                <h2 style="margin: 0 0 10px 0; color: #1f2937; font-size: 20px; font-weight: 600;">Halo {help_request.name} 👋</h2>
                                <p style="margin: 0; color: #6b7280; font-size: 14px; line-height: 1.6;">
                                    Terima kasih telah menghubungi kami. Kami telah menanggapi permintaan bantuan Anda.
                                </p>
                            </td>
                        </tr>
                        
                        <!-- Request Details Box -->
                        <tr>
                            <td style="padding: 0 30px 20px 30px;">
                                <div style="background-color: #f9fafb; border-radius: 10px; padding: 20px; border: 1px solid #e5e7eb;">
                                    <h3 style="margin: 0 0 15px 0; color: #1f2937; font-size: 16px; font-weight: 600; display: flex; align-items: center;">
                                        <span style="margin-right: 8px;">📋</span> Detail Permintaan
                                    </h3>
                                    <table width="100%" cellpadding="0" cellspacing="0">
                                        <tr>
                                            <td style="padding: 8px 0; border-bottom: 1px solid #e5e7eb;">
                                                <span style="color: #6b7280; font-size: 13px;">ID Permintaan</span><br>
                                                <span style="color: #1f2937; font-size: 14px; font-weight: 500;">#{help_request.id}</span>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td style="padding: 8px 0; border-bottom: 1px solid #e5e7eb;">
                                                <span style="color: #6b7280; font-size: 13px;">Jenis Masalah</span><br>
                                                <span style="color: #1f2937; font-size: 14px; font-weight: 500;">{help_request.issue_description}</span>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td style="padding: 8px 0; border-bottom: 1px solid #e5e7eb;">
                                                <span style="color: #6b7280; font-size: 13px;">Status</span><br>
                                                <span style="display: inline-block; background-color: {status['bg']}; color: {status['color']}; padding: 4px 12px; border-radius: 20px; font-size: 13px; font-weight: 600;">
                                                    {status['text']}
                                                </span>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td style="padding: 8px 0; border-bottom: 1px solid #e5e7eb;">
                                                <span style="color: #6b7280; font-size: 13px;">Tanggal Permintaan</span><br>
                                                <span style="color: #1f2937; font-size: 14px;">{help_request.created_at.strftime('%d %B %Y %H:%M')} WIB</span>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td style="padding: 8px 0;">
                                                <span style="color: #6b7280; font-size: 13px;">Tanggal Tanggapan</span><br>
                                                <span style="color: #1f2937; font-size: 14px;">{help_request.response_at.strftime('%d %B %Y %H:%M')} WIB</span>
                                            </td>
                                        </tr>
                                    </table>
                                </div>
                            </td>
                        </tr>
                        
                        <!-- User Message Box -->
                        <tr>
                            <td style="padding: 0 30px 20px 30px;">
                                <div style="background-color: #eff6ff; border-radius: 10px; padding: 20px; border-left: 4px solid #3b82f6;">
                                    <h3 style="margin: 0 0 12px 0; color: #1e40af; font-size: 15px; font-weight: 600; display: flex; align-items: center;">
                                        <span style="margin-right: 8px;">💬</span> Pesan Anda
                                    </h3>
                                    <p style="margin: 0; color: #1e3a8a; font-size: 14px; line-height: 1.6; white-space: pre-wrap;">{help_request.message}</p>
                                </div>
                            </td>
                        </tr>
                        
                        <!-- Admin Response Box -->
                        <tr>
                            <td style="padding: 0 30px 20px 30px;">
                                <div style="background-color: #ecfdf5; border-radius: 10px; padding: 20px; border-left: 4px solid #10b981;">
                                    <h3 style="margin: 0 0 12px 0; color: #065f46; font-size: 15px; font-weight: 600; display: flex; align-items: center;">
                                        <span style="margin-right: 8px;">✅</span> Tanggapan dari Tim Kami
                                    </h3>
                                    <p style="margin: 0; color: #064e3b; font-size: 14px; line-height: 1.6; white-space: pre-wrap;">{help_request.admin_response}</p>
                                </div>
                            </td>
                        </tr>
                        
                        <!-- Contact Info -->
                        <tr>
                            <td style="padding: 0 30px 20px 30px;">
                                <div style="background-color: #fef3c7; border-radius: 10px; padding: 20px; text-align: center;">
                                    <p style="margin: 0 0 10px 0; color: #92400e; font-size: 14px; font-weight: 500;">
                                        Jika Anda memiliki pertanyaan lebih lanjut, jangan hesitate untuk menghubungi kami!
                                    </p>
                                    <p style="margin: 0; color: #78350f; font-size: 13px;">
                                        📧 <strong>Email:</strong> haisen.bussines@gmail.com<br>
                                        ⏰ <strong>Jam Operasional:</strong> Senin - Jumat, 09:00 - 17:00 WIB
                                    </p>
                                </div>
                            </td>
                        </tr>
                        
                        <!-- Footer -->
                        <tr>
                            <td style="background-color: #1f2937; padding: 25px 30px; text-align: center;">
                                <p style="margin: 0 0 8px 0; color: #9ca3af; font-size: 13px;">
                                    Terima kasih atas kepercayaan Anda menggunakan layanan Haisen Official!
                                </p>
                                <p style="margin: 0; color: #6b7280; font-size: 12px;">
                                    © 2024 Haisen Official. All rights reserved.
                                </p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
    
    # Send HTML email
    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = SMTP_EMAIL
        msg['To'] = help_request.email
        msg['Subject'] = subject
        
        # Attach both plain text and HTML versions
        plain_text = f"""
Halo {help_request.name},

Terima kasih telah menghubungi kami. Kami telah menanggapi permintaan bantuan Anda.

Detail Permintaan:
- ID: #{help_request.id}
- Jenis Masalah: {help_request.issue_description}
- Status: {status['text']}
- Tanggal Permintaan: {help_request.created_at.strftime('%d %B %Y %H:%M')} WIB
- Tanggal Tanggapan: {help_request.response_at.strftime('%d %B %Y %H:%M')} WIB

Pesan Anda:
{help_request.message}

Tanggapan dari Tim Kami:
{help_request.admin_response}

Jika ada pertanyaan, hubungi: haisen.bussines@gmail.com

© 2024 Haisen Official
        """
        
        msg.attach(MIMEText(plain_text, 'plain'))
        msg.attach(MIMEText(html_body, 'html'))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False


# ==================== HELPER FUNCTIONS ====================

def slugify(text):
    """Membuat slug aman dari teks"""
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    text = re.sub(r'-+', '-', text).strip('-')
    return text

def create_app_folders(app_title, app_id):
    """
    Membuat folder berdasarkan ID dan Slug Judul (Level Pro)
    Format Folder: {id}-{slug}
    Contoh: 15-super-game
    """
    # Slugify judul
    app_slug = slugify(app_title)
    if not app_slug:
        app_slug = "untitled"
    
    # Gabungkan ID + Slug agar unik
    folder_name = f"{app_id}-{app_slug}"
    
    base_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], folder_name)

    icon_folder = os.path.join(base_folder, "icon")
    file_folder = os.path.join(base_folder, "file")
    screenshots_folder = os.path.join(base_folder, "screenshots")

    # Buat folder jika belum ada
    os.makedirs(icon_folder, exist_ok=True)
    os.makedirs(file_folder, exist_ok=True)
    os.makedirs(screenshots_folder, exist_ok=True)

    return folder_name, icon_folder, file_folder, screenshots_folder

ALLOWED_EXTENSIONS = {
    'png', 'jpg', 'jpeg', 'webp', 'gif',
    'apk', 'zip', 'rar', 'pdf', 'exe'
}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ==================== KONFIGURASI APLIKASI ====================

app = Flask(__name__)
app.config['SECRET_KEY'] = 'haisen-official-secret-key-2024'
# Sesuaikan dengan database Anda
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost:3307/haisen_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Batas ukuran upload (10GB)
TEN_GB = 10 * 1024 * 1024 * 1024
app.config['MAX_CONTENT_LENGTH'] = TEN_GB

# Buat folder uploads utama jika belum ada
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'profiles'), exist_ok=True)

# Inisialisasi Database
db = SQLAlchemy(app)

# Setup Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# ==================== MODELS ====================

class User(UserMixin, db.Model):
    """Model User untuk Admin dan User biasa"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='user')  # 'admin', 'user', atau 'developer'
    is_active = db.Column(db.Boolean, default=True)
    is_approved = db.Column(db.Boolean, default=False)  # Untuk developer approval
    is_temp_password = db.Column(db.Boolean, default=False)  # Flag jika pakai temp password dari admin
    delete_requested = db.Column(db.Boolean, default=False)  # User minta penghapusan akun
    delete_requested_at = db.Column(db.DateTime)  # Waktu request penghapusan
    
    # Profile fields
    profile_photo = db.Column(db.String(500))  # Untuk developer profile photo
    avatar_type = db.Column(db.String(50), default='letter')  # Untuk user: 'letter' atau 'animal'
    developer_description = db.Column(db.Text)  # Deskripsi developer
    social_media = db.Column(db.Text)  # JSON string untuk social media links
    destination_location = db.Column(db.Text)  # Lokasi tujuan user
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    def approve_developer(self):
        """Approve developer dan aktifkan akun"""
        if self.role == 'developer':
            self.is_approved = True
            self.is_active = True
            return True
        return False
    
    def reject_developer(self):
        """Tolak developer dan non-aktifkan akun"""
        if self.role == 'developer':
            self.is_active = False
            self.is_approved = False
            return True
        return False
    
    def is_pending_developer(self):
        """Cek apakah developer yang menunggu approval"""
        return self.role == 'developer' and not self.is_approved and not self.is_active

class Category(db.Model):
    """Model Kategori"""
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    icon = db.Column(db.String(50), default='folder')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    apps = db.relationship('App', backref='category', lazy=True)

class App(db.Model):
    """Model Aplikasi/File (Seperti di Play Store)"""
    __tablename__ = 'apps'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    developer = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # Developer pemilik aplikasi
    version = db.Column(db.String(50))
    size = db.Column(db.String(50))
    price = db.Column(db.String(20), default='Gratis')
    icon = db.Column(db.String(200))
    screenshots = db.Column(db.Text)  # JSON string for multiple screenshots
    file_path = db.Column(db.String(500))
    rating = db.Column(db.Float, default=0.0)
    downloads = db.Column(db.Integer, default=0)
    is_featured = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with reviews
    reviews = db.relationship('Review', backref='app', lazy=True, cascade='all, delete-orphan')
    # Relationship with developer user
    owner = db.relationship('User', backref='apps')

class Review(db.Model):
    """Model Review untuk Rating dan Komentar"""
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    app_id = db.Column(db.Integer, db.ForeignKey('apps.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 rating
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Admin reply fields
    admin_reply = db.Column(db.Text)
    admin_reply_at = db.Column(db.DateTime)
    
    # Lokasi tujuan untuk review
    destination_location = db.Column(db.Text)
    
    # Relationship with user
    user = db.relationship('User', backref='reviews')

class AppUpload(db.Model):
    """Model untuk melacak setiap upload aplikasi oleh developer"""
    __tablename__ = 'app_uploads'
    
    id = db.Column(db.Integer, primary_key=True)
    app_id = db.Column(db.Integer, db.ForeignKey('apps.id'), nullable=False)
    developer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    version = db.Column(db.String(50), nullable=False)
    notes = db.Column(db.Text)  # Catatan tentang update/perubahan
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    app = db.relationship('App', backref='uploads')
    developer = db.relationship('User', backref='uploads')

class AppDownload(db.Model):
    """Model untuk melacak setiap download aplikasi oleh user"""
    __tablename__ = 'app_downloads'
    
    id = db.Column(db.Integer, primary_key=True)
    app_id = db.Column(db.Integer, db.ForeignKey('apps.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    version = db.Column(db.String(50))  # Versi aplikasi yang di-download
    downloaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    app = db.relationship('App', backref='downloads_history')
    user = db.relationship('User', backref='downloads_history')

class UserFollowDeveloper(db.Model):
    """Model untuk melacak developer mana saja yang diikuti user"""
    __tablename__ = 'user_follow_developer'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    developer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    followed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Unique constraint - satu user tidak bisa follow developer yang sama dua kali
    __table_args__ = (db.UniqueConstraint('user_id', 'developer_id', name='unique_user_follow'),)
    
    user = db.relationship('User', foreign_keys=[user_id], backref='following')
    developer = db.relationship('User', foreign_keys=[developer_id], backref='followers')

class Notification(db.Model):
    """Model untuk notifikasi kepada user tentang update aplikasi"""
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    app_id = db.Column(db.Integer, db.ForeignKey('apps.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50))  # 'app_update', 'new_app', 'new_review'
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='notifications')
    app = db.relationship('App', backref='notifications')

class HelpRequest(db.Model):
    """Model untuk menyimpan permohonan bantuan dari user"""
    __tablename__ = 'help_requests'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    issue_type = db.Column(db.String(100), nullable=False)  # 'akun_nonaktif', 'aktivasi_ulang', dll
    issue_description = db.Column(db.String(200))  # Deskripsi singkat jenis masalah
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'in_progress', 'resolved', 'closed'
    admin_response = db.Column(db.Text)  # Balasan dari admin
    response_at = db.Column(db.DateTime)  # Waktu admin merespon
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<HelpRequest {self.id} - {self.issue_type}>'

class MaintenanceRoute(db.Model):
    """Model untuk menyimpan route yang sedang dalam maintenance"""
    __tablename__ = 'maintenance_routes'

    id = db.Column(db.Integer, primary_key=True)
    route_name = db.Column(db.String(200), unique=True, nullable=False)  # Nama route (contoh: 'index', 'admin_dashboard', 'kategori')
    route_path = db.Column(db.String(200), nullable=False)  # Path route (contoh: '/', '/admin', '/kategori')
    is_maintenance = db.Column(db.Boolean, default=False)  # Status maintenance
    maintenance_message = db.Column(db.Text, default='Platform sedang dalam pemeliharaan. Mohon menunggu.')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<MaintenanceRoute {self.route_name}>'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ==================== PUBLIC ROUTES ====================

@app.route('/')
def index():
    """Halaman utama dengan tampilan seperti Play Store"""
    categories = Category.query.all()
    featured_apps = App.query.filter_by(is_featured=True, is_active=True).limit(6).all()
    recent_apps = App.query.filter_by(is_active=True).order_by(App.created_at.desc()).limit(12).all()
    popular_apps = App.query.filter_by(is_active=True).order_by(App.downloads.desc()).limit(10).all()
    
    return render_template('index.html', 
                         categories=categories,
                         featured_apps=featured_apps,
                         recent_apps=recent_apps,
                         popular_apps=popular_apps)
    
@app.template_filter('format_number')
def format_number(value):
    try:
        return "{:,}".format(int(value)).replace(",", ".")
    except (ValueError, TypeError):
        return value

@app.route('/kategori')
@app.route('/kategori/<int:category_id>')
def seluruh_kategori(category_id=None):
    categories = Category.query.all()

    selected_category = None
    apps = []
    apps_by_category = {}

    if category_id:
        selected_category = Category.query.get_or_404(category_id)
        apps = App.query.filter_by(category_id=category_id).order_by(App.downloads.desc()).all()
    else:
        # Ambil semua aplikasi dan kelompokkan berdasarkan kategori
        for category in categories:
            apps_by_category[category.id] = App.query.filter_by(
                category_id=category.id
            ).order_by(App.downloads.desc()).all()

    return render_template(
        'all_categories.html',
        categories=categories,
        selected_category=selected_category,
        apps=apps,
        apps_by_category=apps_by_category
    )


@app.route('/popular-apps')
def seluruh_aplikasi_populer():
    """Halaman semua aplikasi populer"""
    apps = App.query.filter_by(is_active=True).order_by(App.downloads.desc()).all()
    
    # Calculate stats
    total_downloads = sum(app.downloads for app in apps)
    avg_rating = sum(app.rating for app in apps) / len(apps) if apps else 0
    
    return render_template('popular_apps.html', 
                         apps=apps,
                         total_downloads=total_downloads,
                         avg_rating=avg_rating)


@app.route('/category/<int:category_id>')
def category(category_id):
    """Halaman kategori - tampilan seperti Google Drive"""
    cat = Category.query.get_or_404(category_id)
    apps = App.query.filter_by(category_id=category_id, is_active=True).all()
    return render_template('category.html', category=cat, apps=apps)

@app.route('/app/<int:app_id>')
def app_detail(app_id):
    """Halaman detail aplikasi"""
    app = App.query.get_or_404(app_id)
    reviews = Review.query.filter_by(app_id=app_id).order_by(Review.created_at.desc()).all()
    related_apps = App.query.filter_by(category_id=app.category_id, is_active=True).filter(App.id != app_id).limit(4).all()
    
    # Check if current user has already reviewed
    user_review = None
    user_following_developer = False
    user_last_download = None
    
    if current_user.is_authenticated:
        user_review = Review.query.filter_by(app_id=app_id, user_id=current_user.id).first()
        
        # Check if following developer
        if app.user_id:
            user_following_developer = UserFollowDeveloper.query.filter_by(
                user_id=current_user.id,
                developer_id=app.user_id
            ).first() is not None
        
        # Get user's last download of this app
        user_last_download = AppDownload.query.filter_by(
            app_id=app_id,
            user_id=current_user.id
        ).order_by(AppDownload.downloaded_at.desc()).first()
    
    return render_template('app_detail.html', 
                         app=app, 
                         related_apps=related_apps, 
                         reviews=reviews, 
                         user_review=user_review,
                         user_following_developer=user_following_developer,
                         user_last_download=user_last_download)

@app.route('/app/<int:app_id>/review', methods=['POST'])
@login_required
def submit_review(app_id):
    """Submit review and rating for an app"""
    app = App.query.get_or_404(app_id)
    
    rating = request.form.get('rating', type=int)
    comment = request.form.get('comment', '').strip()
    
    if not rating or rating < 1 or rating > 5:
        flash('Rating harus antara 1-5 bintang', 'error')
        return redirect(url_for('app_detail', app_id=app_id))
    
    existing_review = Review.query.filter_by(app_id=app_id, user_id=current_user.id).first()
    
    if existing_review:
        existing_review.rating = rating
        existing_review.comment = comment
        flash('Review berhasil diperbarui!', 'success')
    else:
        review = Review(
            app_id=app_id,
            user_id=current_user.id,
            rating=rating,
            comment=comment
        )
        db.session.add(review)
        flash('Terima kasih atas review Anda!', 'success')
    
    # Update app's average rating
    reviews = Review.query.filter_by(app_id=app_id).all()
    if reviews:
        total_rating = sum(r.rating for r in reviews)
        app.rating = round(total_rating / len(reviews), 1)
    
    db.session.commit()
    return redirect(url_for('app_detail', app_id=app_id))

@app.route('/app/<int:app_id>/review/delete/<int:review_id>')
@login_required
def delete_review(app_id, review_id):
    """Delete user's own review"""
    review = Review.query.get_or_404(review_id)
    
    if review.user_id != current_user.id and current_user.role != 'admin':
        flash('Anda tidak memiliki izin untuk menghapus review ini', 'error')
        return redirect(url_for('app_detail', app_id=app_id))
    
    app = App.query.get_or_404(app_id)
    db.session.delete(review)
    
    # Update app's average rating
    reviews = Review.query.filter_by(app_id=app_id).all()
    if reviews:
        total_rating = sum(r.rating for r in reviews)
        app.rating = round(total_rating / len(reviews), 1)
    else:
        app.rating = 0.0
    
    db.session.commit()
    flash('Review berhasil dihapus', 'success')
    return redirect(url_for('app_detail', app_id=app_id))

@app.route('/download/<int:app_id>')
@login_required
def download(app_id):
    app_data = App.query.get_or_404(app_id)
    app_data.downloads += 1
    
    # Check if user already has this app downloaded - update instead of creating new record
    existing_download = AppDownload.query.filter_by(
        app_id=app_id,
        user_id=current_user.id
    ).first()
    
    if existing_download:
        # Update existing record with new version and download date
        existing_download.version = app_data.version
        existing_download.downloaded_at = datetime.utcnow()
    else:
        # Create new download record only if first download
        download_record = AppDownload(
            app_id=app_id,
            user_id=current_user.id,
            version=app_data.version
        )
        db.session.add(download_record)
    
    db.session.commit()

    if app_data.file_path:
        return send_from_directory(
            current_app.config['UPLOAD_FOLDER'],
            app_data.file_path,
            as_attachment=True,
            conditional=True
        )
    flash('File tidak tersedia', 'error')
    return redirect(url_for('app_detail', app_id=app_id))

@app.route('/search')
def search():
    """Pencarian - tampilan seperti Google Drive"""
    query = request.args.get('q', '')
    if query:
        apps = App.query.filter(
            (App.title.contains(query)) | 
            (App.description.contains(query)) |
            (App.developer.contains(query)),
            App.is_active == True
        ).all()
    else:
        apps = []
    return render_template('search.html', apps=apps, query=query)

@app.route('/layanan')
def layanan_index():
    """Halaman utama layanan bantuan"""
    return render_template('layanan/index.html')

@app.route('/layanan/<service_type>')
def layanan(service_type):
    """Halaman form layanan berdasarkan jenis masalah"""
    
    # Mapping jenis layanan
    services = {
        'akun_nonaktif': {
            'title': 'Akun Dinonaktifkan',
            'icon': 'bi-person-x',
            'description': 'Permohonan pengaktifan kembali akun yang telah dinonaktifkan',
            'placeholder': 'Jelaskan mengapa akun Anda dinonaktifkan dan kapan terakhir Anda dapat mengakses akun...'
        },
        'aktivasi_ulang': {
            'title': 'Aktivasi Ulang Akun',
            'icon': 'bi-arrow-clockwise',
            'description': 'Permohonan aktivasi ulang akun yang tidak aktif',
            'placeholder': 'Jelaskan mengapa Anda meminta aktivasi ulang dan informasi akun Anda...'
        },
        'lupa_password': {
            'title': 'Lupa Password',
            'icon': 'bi-key',
            'description': 'Bantuan untuk mereset kata sandi akun Anda',
            'placeholder': 'Masukkan email yang terdaftar dan kami akan membantu mereset password Anda...'
        },
        'lupa_username': {
            'title': 'Lupa Username',
            'icon': 'bi-person-badge',
            'description': 'Bantuan untuk mengingat atau mendapatkan username',
            'placeholder': 'Masukkan email yang terdaftar untuk mendapatkan bantuan username Anda...'
        },
        'verifikasi': {
            'title': 'Verifikasi Akun',
            'icon': 'bi-patch-check',
            'description': 'Masalah terkait verifikasi identitas akun',
            'placeholder': 'Jelaskan masalah verifikasi yang Anda hadapi...'
        },
        'hapus_akun': {
            'title': 'Hapus Akun',
            'icon': 'bi-trash',
            'description': 'Permohonan penghapusan akun secara permanen',
            'placeholder': 'Jelaskan mengapa Anda ingin menghapus akun dan tunggu konfirmasi dari tim kami...'
        },
        'kendala_teknis': {
            'title': 'Kendala Teknis',
            'icon': 'bi-gear',
            'description': 'Masalah teknis dengan aplikasi atau sistem',
            'placeholder': 'Jelaskan masalah teknis yang Anda alami secara detail...'
        },
        'lainnya': {
            'title': 'Layanan Lainnya',
            'icon': 'bi-three-dots',
            'description': 'Pertanyaan atau masalah lainnya',
            'placeholder': 'Jelaskan pertanyaan atau masalah Anda...'
        }
    }
    
    if service_type not in services:
        flash('Layanan tidak ditemukan', 'error')
        return redirect(url_for('layanan_index'))
    
    service = services[service_type]
    
    return render_template('layanan/form.html',
                         service_type=service_type,
                         service_title=service['title'],
                         service_icon=service['icon'],
                         service_description=service['description'],
                         service_placeholder=service['placeholder'])

@app.route('/help')
def help_center():
    """Halaman layanan bantuan - redirect ke layanan"""
    return redirect(url_for('layanan_index'))

@app.route('/help/submit', methods=['POST'])
def submit_help_request():
    """Submit permohonan bantuan dari form"""
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    issue_type = request.form.get('issue_type', '')
    message = request.form.get('message', '').strip()

    # Validasi input
    if not name or not email or not issue_type or not message:
        flash('Mohon lengkapi semua field yang diperlukan', 'error')
        return redirect(url_for('help_center'))

    # Validasi email
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        flash('Format email tidak valid', 'error')
        return redirect(url_for('help_center'))

    # Mapping jenis masalah ke deskripsi
    issue_descriptions = {
        'akun_nonaktif': 'Akun Dinonaktifkan',
        'aktivasi_ulang': 'Permohonan Aktivasi Ulang',
        'lupa_password': 'Lupa Password',
        'lupa_username': 'Lupa Username',
        'verifikasi': 'Masalah Verifikasi Akun',
        'hapus_akun': 'Permohonan Hapus Akun',
        'kendala_teknis': 'Kendala Teknis',
        'lainnya': 'Lainnya'
    }

    issue_desc = issue_descriptions.get(issue_type, 'Lainnya')

    # Buat record di database
    help_request = HelpRequest(
        name=name,
        email=email,
        issue_type=issue_type,
        issue_description=issue_desc,
        message=message,
        status='pending'
    )
    db.session.add(help_request)
    db.session.commit()

    # Buat pesan email
    subject = f"Permohonan Bantuan - {issue_desc} - {name}"

    body = f"""
    Halo Tim Haisen Official,

    Terima kasih telah menghubungi kami. Berikut adalah detail permohonan bantuan Anda:

    ─────────────────────────────────────
    Nama: {name}
    Email: {email}
    Jenis Masalah: {issue_desc}
    ─────────────────────────────────────

    Pesan:
    {message}

    ─────────────────────────────────────

    Tim kami akan memproses permohonan Anda secepat mungkin. Harap tunggu respon dalam 24-48 jam kerja.

    Salam hangat,
    {name}
    """

    # Kirim email
    if send_email(email, subject, body):
        flash('✅ Permohonan bantuan berhasil dikirim! Kami akan menghubungi Anda segera.', 'success')
    else:
        flash('❌ Gagal mengirim permohonan bantuan. Silakan coba lagi atau hubungi kami via email langsung.', 'error')

    return redirect(url_for('help_center'))



# ==================== DEVELOPERS LIST ROUTES ====================

@app.route('/developers')
def developers():
    """Halaman daftar semua developer"""
    # Get all approved developers
    developer_users = User.query.filter_by(role='developer', is_approved=True, is_active=True).all()
    
    # Get app count and total downloads for each developer
    developer_data = []
    for dev in developer_users:
        apps = App.query.filter_by(user_id=dev.id, is_active=True).all()
        total_downloads = sum(app.downloads for app in apps)
        developer_data.append({
            'developer': dev,
            'app_count': len(apps),
            'total_downloads': total_downloads
        })
    
    return render_template('developers.html', developer_data=developer_data)

@app.route('/developer/<int:developer_id>')
def developer_detail(developer_id):
    """Halaman detail developer dengan daftar aplikasi"""
    developer = User.query.get_or_404(developer_id)
    
    # Verify this is a developer
    if developer.role != 'developer':
        flash('User ini bukan developer', 'error')
        return redirect(url_for('index'))
    
    # Get all apps by this developer
    apps = App.query.filter_by(user_id=developer_id, is_active=True).order_by(App.created_at.desc()).all()
    
    # Get follower count
    follower_count = UserFollowDeveloper.query.filter_by(developer_id=developer_id).count()
    
    # Check if current user is following
    is_following = False
    if current_user.is_authenticated:
        is_following = UserFollowDeveloper.query.filter_by(
            user_id=current_user.id,
            developer_id=developer_id
        ).first() is not None
    
    return render_template('developer_detail.html', 
                         developer=developer,
                         apps=apps,
                         follower_count=follower_count,
                         is_following=is_following)

# ==================== AUTH ROUTES ====================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif current_user.role == 'developer' and current_user.is_approved:
            return redirect(url_for('developer_apps'))
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            if user.is_active:
                login_user(user)
                
                # Check jika user punya temporary password
                if user.is_temp_password:
                    flash('⚠️ Anda menggunakan password sementara dari admin. Harap ubah password Anda sekarang untuk keamanan akun!', 'warning')
                    return redirect(url_for('change_password'))
                
                if user.role == 'admin':
                    return redirect(url_for('admin_dashboard'))
                elif user.role == 'developer' and user.is_approved:
                    return redirect(url_for('developer_dashboard'))
                return redirect(url_for('index'))
            else:
                flash('Akun Anda dinonaktifkan', 'error')
        else:
            flash('Username atau password salah', 'error')
    
    return render_template('login.html')

@app.route('/admin-temp-login', methods=['GET', 'POST'])
def admin_temp_login():
    """Temporary login page for admin when login route is under maintenance"""
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        logout_user()
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            if user.role == 'admin' and user.is_active:
                login_user(user)
                
                # Check jika user punya temporary password
                if user.is_temp_password:
                    flash('⚠️ Anda menggunakan password sementara dari admin. Harap ubah password Anda sekarang untuk keamanan akun!', 'warning')
                    return redirect(url_for('change_password'))
                
                return redirect(url_for('admin_dashboard'))
            elif user.role != 'admin':
                flash('❌ Hanya Admin yang dapat login di sini selama maintenance', 'error')
            else:
                flash('Akun Anda dinonaktifkan', 'error')
        else:
            flash('Username atau password salah', 'error')
    
    return render_template('admin_temp_login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        role = request.form.get('role', 'user')
        
        # Validasi role
        if role not in ['user', 'developer']:
            flash('Jenis akun tidak valid', 'error')
            return render_template('register.html')
        
        # Validasi username (minimal 3 karakter)
        if not username or len(username) < 3:
            flash('Username minimal 3 karakter', 'error')
            return render_template('register.html')
        
        # Validasi username
        if User.query.filter_by(username=username).first():
            flash('Username sudah digunakan', 'error')
            return render_template('register.html')
        
        # Validasi email
        if not email or '@' not in email:
            flash('Email tidak valid', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email sudah terdaftar', 'error')
            return render_template('register.html')
        
        # Buat user baru
        user = User(username=username, email=email, role=role)
        
        # Jika developer, gunakan password default dan kirim via email
        if role == 'developer':
            # Gunakan password default
            default_password = "password123"
            user.set_password(default_password)
            user.is_active = False
            user.is_approved = False
            db.session.add(user)
            db.session.commit()
            
            # Kirim email dengan credentials
            subject = "Registrasi Developer - Haisen Official"
            body = f"""
            Halo {username},

            Terima kasih telah mendaftar sebagai developer di Haisen Official.

            Berikut adalah informasi akun Anda:
            ─────────────────────────────────────
            Username: {username}
            Email: {email}
            Password: {default_password}
            ─────────────────────────────────────

            Akun Anda sedang menunggu persetujuan admin. Setelah disetujui, Anda dapat:
            ✓ Login ke akun developer Anda
            ✓ Mengupload aplikasi ke platform Haisen Official
            ✓ Mengelola aplikasi yang Anda publikasikan

            Silakan login melalui link berikut:
            {url_for('login', _external=True)}

            Jika Anda memiliki pertanyaan, jangan hesitate untuk menghubungi kami.

            Best regards,
            Tim Haisen Official
            """
            
            # Kirim email
            if send_email(email, subject, body):
                flash('✅ Registrasi berhasil! 🎉 Akun developer Anda sedang menunggu persetujuan admin. Email dengan credentials telah dikirim ke Anda.', 'success')
            else:
                flash('✅ Registrasi berhasil! 🎉 Akun developer Anda sedang menunggu persetujuan admin. (Gagal mengirim email, silakan hubungi admin)', 'warning')
            
            return redirect(url_for('login'))
        else:
            # User biasa - gunakan password yang diinput
            if not password:
                flash('Password wajib diisi', 'error')
                return render_template('register.html')
            
            if len(password) < 6:
                flash('Password minimal 6 karakter', 'error')
                return render_template('register.html')
            
            if password != confirm_password:
                flash('Password tidak cocok', 'error')
                return render_template('register.html')
            
            user.set_password(password)
            user.is_active = True
            user.is_approved = True
            db.session.add(user)
            db.session.commit()
            flash('✅ Registrasi berhasil! Silakan login', 'success')
            return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Anda telah logout', 'success')
    return redirect(url_for('index'))

# ==================== ACCOUNT MANAGEMENT ROUTES ====================

@app.route('/profile')
@login_required
def profile():
    """Halaman profil user"""
    return render_template('profile.html', user=current_user)

@app.route('/developer/<int:developer_id>')
def developer_profile(developer_id):
    """Halaman detail profil developer - public"""
    developer = User.query.filter_by(id=developer_id, role='developer', is_active=True, is_approved=True).first_or_404()
    
    # Get developer's apps
    apps = App.query.filter_by(user_id=developer_id, is_active=True).all()
    followers_count = UserFollowDeveloper.query.filter_by(developer_id=developer_id).count()
    
    # Parse social media if exists
    social_media = {}
    if developer.social_media:
        try:
            import json
            social_media = json.loads(developer.social_media)
        except:
            pass
    
    return render_template('developer_profile.html', 
                         developer=developer,
                         apps=apps,
                         followers_count=followers_count,
                         social_media=social_media)

@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Edit profil user atau developer"""
    if request.method == 'POST':
        try:
            # Update username dan email (hanya jika berbeda)
            new_username = request.form.get('username', current_user.username)
            new_email = request.form.get('email', current_user.email)
            
            # Cek apakah username sudah digunakan
            if new_username != current_user.username:
                existing = User.query.filter_by(username=new_username).first()
                if existing:
                    flash('❌ Username sudah digunakan', 'error')
                    return render_template('edit_profile.html', user=current_user)
                current_user.username = new_username
            
            # Cek apakah email sudah digunakan
            if new_email != current_user.email:
                existing = User.query.filter_by(email=new_email).first()
                if existing:
                    flash('❌ Email sudah digunakan', 'error')
                    return render_template('edit_profile.html', user=current_user)
            
            # Update avatar untuk user
            if current_user.role == 'user':
                avatar_type = request.form.get('avatar_type', 'letter')
                current_user.avatar_type = avatar_type
            
            # Update profile untuk developer
            if current_user.role == 'developer':
                current_user.developer_description = request.form.get('developer_description', '')
                
                # Upload profile photo
                if 'profile_photo' in request.files:
                    file = request.files['profile_photo']
                    if file and file.filename and allowed_file(file.filename):
                        # Delete old photo if exists
                        if current_user.profile_photo:
                            old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'profiles', current_user.profile_photo)
                            if os.path.exists(old_path):
                                os.remove(old_path)
                        
                        # Save new photo
                        os.makedirs(os.path.join(current_app.config['UPLOAD_FOLDER'], 'profiles'), exist_ok=True)
                        filename = f"dev_{current_user.id}_{uuid.uuid4().hex}_{secure_filename(file.filename)}"
                        file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], 'profiles', filename))
                        current_user.profile_photo = filename
                
                # Update social media
                social_media_data = {}
                for key in ['instagram', 'twitter', 'github', 'linkedin', 'website']:
                    value = request.form.get(f'social_{key}', '')
                    if value:
                        social_media_data[key] = value
                
                import json
                current_user.social_media = json.dumps(social_media_data) if social_media_data else None
            
            db.session.commit()
            flash('✅ Profil berhasil diperbarui!', 'success')
            return redirect(url_for('profile'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Terjadi kesalahan: {str(e)}', 'error')
            return render_template('edit_profile.html', user=current_user)
    
    # Parse social media for display
    social_media = {}
    if current_user.social_media:
        try:
            import json
            social_media = json.loads(current_user.social_media)
        except:
            pass
    
    return render_template('edit_profile.html', user=current_user, social_media=social_media)

@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Route untuk ubah password"""
    if request.method == 'POST':
        current_pwd = request.form.get('current_password')
        new_pwd = request.form.get('new_password')
        confirm_pwd = request.form.get('confirm_password')
        
        # Validasi
        if not current_user.check_password(current_pwd):
            flash('❌ Password saat ini tidak benar', 'error')
            return render_template('change_password.html')
        
        if new_pwd != confirm_pwd:
            flash('❌ Password baru tidak cocok', 'error')
            return render_template('change_password.html')
        
        if len(new_pwd) < 6:
            flash('❌ Password minimal 6 karakter', 'error')
            return render_template('change_password.html')
        
        # Update password
        current_user.set_password(new_pwd)
        current_user.is_temp_password = False  # Hapus flag temp password
        db.session.commit()
        
        flash('✅ Password berhasil diubah! Silakan login kembali dengan password baru.', 'success')
        logout_user()
        return redirect(url_for('login'))
    
    return render_template('change_password.html')

@app.route('/change-email', methods=['GET', 'POST'])
@login_required
def change_email():
    """Route untuk ubah email"""
    if request.method == 'POST':
        new_email = request.form.get('new_email').strip().lower()
        password = request.form.get('password')
        
        # Validasi
        if not current_user.check_password(password):
            flash('❌ Password tidak benar', 'error')
            return render_template('change_email.html')
        
        # Cek email sudah digunakan
        if User.query.filter_by(email=new_email).filter(User.id != current_user.id).first():
            flash('❌ Email sudah terdaftar di sistem', 'error')
            return render_template('change_email.html')
        
        # Update email
        old_email = current_user.email
        current_user.email = new_email
        db.session.commit()
        
        flash(f'✅ Email berhasil diubah dari {old_email} ke {new_email}!', 'success')
        return redirect(url_for('profile'))
    
    return render_template('change_email.html', user=current_user)

@app.route('/delete-account-request', methods=['GET', 'POST'])
@login_required
def delete_account_request():
    """Permohonan penghapusan akun"""
    if request.method == 'POST':
        password = request.form.get('password')
        
        # Validasi password
        if not current_user.check_password(password):
            flash('❌ Password tidak benar', 'error')
            return render_template('delete_account_request.html')
        
        # Tandai untuk penghapusan
        current_user.delete_requested = True
        current_user.delete_requested_at = datetime.utcnow()
        db.session.commit()
        
        flash('✅ Permohonan penghapusan akun Anda telah dikirim. Admin akan memproses permintaan ini dalam 24-48 jam.', 'success')
        logout_user()
        return redirect(url_for('index'))
    
    return render_template('delete_account_request.html', user=current_user)

@app.route('/create-admin', methods=['GET', 'POST'])
def create_admin():
    admin_exists = User.query.filter_by(role='admin').first()
    if admin_exists:
        flash('Admin sudah ada! Silakan login', 'warning')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Password tidak cocok', 'error')
            return render_template('create_admin.html')
        
        admin = User(username=username, email=email, role='admin')
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
        flash('Master Admin berhasil dibuat! Silakan login', 'success')
        return redirect(url_for('login'))
    
    return render_template('create_admin.html')

# ==================== ADMIN ROUTES ====================

@app.route('/admin')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Akses ditolak', 'error')
        return redirect(url_for('index'))
    
    total_apps = App.query.count()
    total_users = User.query.filter_by(role='user').count()
    total_downloads = db.session.query(func.sum(App.downloads)).scalar() or 0
    recent_apps = App.query.order_by(App.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         total_apps=total_apps,
                         total_users=total_users,
                         total_downloads=total_downloads,
                         recent_apps=recent_apps)

@app.route('/admin/apps')
@login_required
def admin_apps():
    if current_user.role != 'admin':
        flash('Akses ditolak', 'error')
        return redirect(url_for('index'))
    apps = App.query.order_by(App.created_at.desc()).all()
    return render_template('admin/apps.html', apps=apps)

@app.route('/admin/apps/add', methods=['GET', 'POST'])
@login_required
def admin_app_add():
    if current_user.role != 'admin':
        abort(403)

    categories = Category.query.all()

    if request.method == 'POST':
        try:
            title = request.form.get('title')
            
            # ✅ VALIDASI TITLE KOSONG
            if not title:
                flash("Judul wajib diisi!", "danger")
                return render_template('admin/app_form.html', categories=categories)

            description = request.form.get('description')
            category_id = request.form.get('category_id')
            category_id = int(category_id) if category_id else None

            version = request.form.get('version')
            developer = request.form.get('developer')
            size = request.form.get('size')
            price = request.form.get('price')
            is_featured = True if request.form.get('is_featured') else False

            # ✅ LEVEL PRO: COMMIT DULU UNTUK DAPAT ID
            app_new = App(
                title=title,
                description=description,
                category_id=category_id,
                version=version,
                developer=developer,
                size=size,
                price=price,
                is_featured=is_featured,
                rating=0.0
            )
            db.session.add(app_new)
            db.session.commit() 

            # ================= BUAT FOLDER (Menggunakan ID yang baru dibuat) =================
            app_slug, icon_folder, file_folder, screenshots_folder = create_app_folders(app_new.title, app_new.id)

            # ================= ICON =================
            icon_file = request.files.get('icon')
            icon_filename = None
            if icon_file and icon_file.filename and allowed_file(icon_file.filename):
                filename = f"{uuid.uuid4().hex}_{secure_filename(icon_file.filename)}"
                icon_file.save(os.path.join(icon_folder, filename))
                icon_filename = f"{app_slug}/icon/{filename}"

            # ================= FILE =================
            file_upload = request.files.get('file_path')
            file_filename = None
            if file_upload and file_upload.filename and allowed_file(file_upload.filename):
                filename = f"{uuid.uuid4().hex}_{secure_filename(file_upload.filename)}"
                file_upload.save(os.path.join(file_folder, filename))
                file_filename = f"{app_slug}/file/{filename}"

            # ================= SCREENSHOTS =================
            screenshot_files = request.files.getlist('screenshots')
            screenshot_names = []
            for file in screenshot_files:
                if file and file.filename and allowed_file(file.filename):
                    filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
                    file.save(os.path.join(screenshots_folder, filename))
                    screenshot_names.append(f"{app_slug}/screenshots/{filename}")

            screenshots_string = ",".join(screenshot_names) if screenshot_names else None

            # ================= UPDATE DB DENGAN PATH FILE =================
            app_new.icon = icon_filename
            app_new.file_path = file_filename
            app_new.screenshots = screenshots_string
            db.session.commit()

            flash("App berhasil ditambahkan!", "success")
            return redirect(url_for('admin_apps'))

        except Exception as e:
            db.session.rollback()
            flash(f"Terjadi kesalahan: {str(e)}", "danger")

    return render_template('admin/app_form.html', categories=categories)

@app.route('/admin/apps/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_app_edit(id):
    if current_user.role != 'admin':
        abort(403)

    app_edit = App.query.get_or_404(id)
    categories = Category.query.all()

    if request.method == 'POST':
        try:
            title = request.form.get('title')

            # ✅ VALIDASI TITLE KOSONG
            if not title:
                flash("Judul wajib diisi!", "danger")
                return render_template('admin/app_form.html', app=app_edit, categories=categories)

            app_edit.title = title
            app_edit.description = request.form.get('description')

            category_id = request.form.get('category_id')
            app_edit.category_id = int(category_id) if category_id else None

            app_edit.version = request.form.get('version')
            app_edit.developer = request.form.get('developer')
            app_edit.size = request.form.get('size')

            # ================= LOGIKA RENAME FOLDER (LEVEL PRO) =================
            
            # 1. Cari nama folder lama dari path yang ada di DB
            old_folder_name = None
            if app_edit.icon:
                old_folder_name = app_edit.icon.split('/')[0]
            elif app_edit.file_path:
                old_folder_name = app_edit.file_path.split('/')[0]
            elif app_edit.screenshots:
                # Ambil dari screenshot pertama
                old_folder_name = app_edit.screenshots.split(',')[0].split('/')[0]

            # 2. Generate nama folder baru berdasarkan ID + Title Baru
            new_slug = slugify(title)
            if not new_slug: new_slug = "untitled"
            new_folder_name = f"{app_edit.id}-{new_slug}"

            # 3. Jika folder lama ada DAN namanya berubah -> RENAME FOLDER
            # Kenapa rename? Agar file yang sudah diupload tidak hilang.
            if old_folder_name and old_folder_name != new_folder_name:
                old_path = os.path.join(app.config['UPLOAD_FOLDER'], old_folder_name)
                new_path = os.path.join(app.config['UPLOAD_FOLDER'], new_folder_name)
                
                if os.path.exists(old_path):
                    # Rename folder fisik
                    os.rename(old_path, new_path)
                    
                    # Update path string di database (replace nama folder lama dengan baru)
                    if app_edit.icon:
                        app_edit.icon = app_edit.icon.replace(old_folder_name, new_folder_name, 1)
                    if app_edit.file_path:
                        app_edit.file_path = app_edit.file_path.replace(old_folder_name, new_folder_name, 1)
                    if app_edit.screenshots:
                        app_edit.screenshots = app_edit.screenshots.replace(old_folder_name, new_folder_name)

            # ================= SET PATH FOLDER SAAT INI =================
            base_folder = os.path.join(app.config['UPLOAD_FOLDER'], new_folder_name)
            icon_folder = os.path.join(base_folder, "icon")
            file_folder = os.path.join(base_folder, "file")
            screenshots_folder = os.path.join(base_folder, "screenshots")
            
            # Pastikan folder ada (jika sebelumnya belum ada file sama sekali)
            os.makedirs(icon_folder, exist_ok=True)
            os.makedirs(file_folder, exist_ok=True)
            os.makedirs(screenshots_folder, exist_ok=True)

            # ================= UPDATE ICON (Jika upload baru) =================
            icon_file = request.files.get('icon')
            if icon_file and icon_file.filename and allowed_file(icon_file.filename):
                if app_edit.icon:
                    old_path = os.path.join(app.config['UPLOAD_FOLDER'], app_edit.icon)
                    if os.path.exists(old_path):
                        os.remove(old_path)

                filename = f"{uuid.uuid4().hex}_{secure_filename(icon_file.filename)}"
                icon_file.save(os.path.join(icon_folder, filename))
                app_edit.icon = f"{new_folder_name}/icon/{filename}"

            # ================= UPDATE FILE (Jika upload baru) =================
            file_upload = request.files.get('file_path')
            if file_upload and file_upload.filename and allowed_file(file_upload.filename):
                if app_edit.file_path:
                    old_path = os.path.join(app.config['UPLOAD_FOLDER'], app_edit.file_path)
                    if os.path.exists(old_path):
                        os.remove(old_path)

                filename = f"{uuid.uuid4().hex}_{secure_filename(file_upload.filename)}"
                file_upload.save(os.path.join(file_folder, filename))
                app_edit.file_path = f"{new_folder_name}/file/{filename}"

            # ================= SCREENSHOTS (Jika upload baru) =================
            screenshot_files = request.files.getlist('screenshots')
            new_screenshots = []

            for file in screenshot_files:
                if file and file.filename and allowed_file(file.filename):
                    filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
                    file.save(os.path.join(screenshots_folder, filename))
                    new_screenshots.append(f"{new_folder_name}/screenshots/{filename}")

            if new_screenshots:
                existing = app_edit.screenshots.split(',') if app_edit.screenshots else []
                # Pastikan existing path sudah menggunakan nama folder baru
                existing = [s.replace(old_folder_name, new_folder_name) for s in existing] if old_folder_name else existing
                
                app_edit.screenshots = ",".join(existing + new_screenshots)

            db.session.commit()
            flash("App berhasil diupdate!", "success")
            return redirect(url_for('admin_apps'))

        except Exception as e:
            db.session.rollback()
            flash(f"Error: {str(e)}", "danger")

    return render_template('admin/app_form.html', app=app_edit, categories=categories)

@app.route('/admin/app/delete/<int:app_id>')
@login_required
def admin_app_delete(app_id):
    if current_user.role != 'admin':
        abort(403)

    app_del = App.query.get_or_404(app_id)

    # Cari nama folder untuk dihapus
    folder_name = None
    if app_del.icon:
        folder_name = app_del.icon.split('/')[0]
    elif app_del.file_path:
        folder_name = app_del.file_path.split('/')[0]
    
    if folder_name:
        folder_path = os.path.join(app.config['UPLOAD_FOLDER'], folder_name)
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)

    db.session.delete(app_del)
    db.session.commit()

    flash('Aplikasi berhasil dihapus', 'success')
    return redirect(url_for('admin_apps'))

@app.route('/admin/categories')
@login_required
def admin_categories():
    if current_user.role != 'admin':
        flash('Akses ditolak', 'error')
        return redirect(url_for('index'))
    categories = Category.query.order_by(Category.created_at.desc()).all()
    return render_template('admin/categories.html', categories=categories)

@app.route('/admin/category/add', methods=['GET', 'POST'])
@login_required
def admin_category_add():
    if current_user.role != 'admin':
        flash('Akses ditolak', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        icon = request.form.get('icon')
        
        category = Category(name=name, description=description, icon=icon)
        db.session.add(category)
        db.session.commit()
        flash('Kategori berhasil ditambahkan', 'success')
        return redirect(url_for('admin_categories'))
    
    return render_template('admin/category_form.html', category=None)

@app.route('/admin/category/edit/<int:category_id>', methods=['GET', 'POST'])
@login_required
def admin_category_edit(category_id):
    if current_user.role != 'admin':
        flash('Akses ditolak', 'error')
        return redirect(url_for('index'))
    
    category = Category.query.get_or_404(category_id)
    
    if request.method == 'POST':
        category.name = request.form.get('name')
        category.description = request.form.get('description')
        category.icon = request.form.get('icon')
        db.session.commit()
        flash('Kategori berhasil diperbarui', 'success')
        return redirect(url_for('admin_categories'))
    
    return render_template('admin/category_form.html', category=category)


@app.route('/admin/category/delete/<int:category_id>', methods=['POST'])
@login_required
def admin_category_delete(category_id):
    if current_user.role != 'admin':
        flash('Akses ditolak', 'error')
        return redirect(url_for('index'))
    
    category = Category.query.get_or_404(category_id)

    # Cegah hapus kalau masih ada aplikasi
    if category.apps:
        flash('Kategori tidak bisa dihapus karena masih memiliki aplikasi.', 'danger')
        return redirect(url_for('admin_categories'))

    db.session.delete(category)
    db.session.commit()

    flash('Kategori berhasil dihapus', 'success')
    return redirect(url_for('admin_categories'))

@app.route('/admin/users')
@login_required
def admin_users():
    if current_user.role != 'admin':
        flash('Akses ditolak', 'error')
        return redirect(url_for('index'))
    # Support optional role filter via query param: ?role=all|user|developer|admin
    role_filter = request.args.get('role', 'all')
    if role_filter in ('user', 'developer', 'admin'):
        users = User.query.filter_by(role=role_filter).order_by(User.created_at.desc()).all()
    else:
        users = User.query.order_by(User.created_at.desc()).all()

    # counts for quick overview
    counts = {
        'all': User.query.count(),
        'user': User.query.filter_by(role='user').count(),
        'developer': User.query.filter_by(role='developer').count(),
        'admin': User.query.filter_by(role='admin').count(),
    }

    return render_template('admin/users.html', users=users, role_filter=role_filter, counts=counts)

@app.route('/admin/user/toggle/<int:user_id>', methods=['GET', 'POST'])
@login_required
def admin_user_toggle(user_id):
    if current_user.role != 'admin':
        flash('Akses ditolak', 'error')
        return redirect(url_for('index'))
    
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    flash(f'User {user.username} {"diaktifkan" if user.is_active else "dinonaktifkan"}', 'success')
    return redirect(url_for('admin_users'))


@app.route('/admin/user/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_user(user_id):
    if current_user.role != 'admin':
        flash('Akses ditolak', 'error')
        return redirect(url_for('index'))
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        username = request.form.get('username', user.username).strip()
        email = request.form.get('email', user.email).strip()
        password = request.form.get('password', '').strip()
        role = request.form.get('role', user.role)

        # Simple uniqueness checks
        if username != user.username:
            if User.query.filter_by(username=username).first():
                flash('Username sudah digunakan', 'error')
                return render_template('admin/edit_user.html', user=user)
            user.username = username
        if email != user.email:
            if User.query.filter_by(email=email).first():
                flash('Email sudah digunakan', 'error')
                return render_template('admin/edit_user.html', user=user)
            user.email = email

        # Do not modify destination_location here (removed form field)
        # Update role
        user.role = role

        # Update password if provided
        if password:
            user.set_password(password)
            user.is_temp_password = False
        db.session.commit()
        flash('Data pengguna berhasil diperbarui', 'success')
        return redirect(url_for('admin_users'))

    return render_template('admin/edit_user.html', user=user)


@app.route('/admin/user/location/<int:user_id>')
@login_required
def admin_user_location(user_id):
    if current_user.role != 'admin':
        flash('Akses ditolak', 'error')
        return redirect(url_for('index'))
    user = User.query.get_or_404(user_id)
    # If no destination stored, redirect back to the user list and jump to the user card
    if not user.destination_location:
        flash('Tidak ada lokasi tersimpan untuk pengguna ini. Mengarahkan ke daftar pengguna.', 'info')
        return redirect(url_for('admin_users') + f"#user-{user.id}")
    return render_template('admin/view_location.html', location=user.destination_location, back='user', obj_id=user.id)

@app.route('/admin/developer-requests')
@login_required
def admin_developer_requests():
    """Halaman untuk melihat dan mengelola permintaan developer"""
    if current_user.role != 'admin':
        flash('Akses ditolak', 'error')
        return redirect(url_for('index'))
    
    # Ambil semua developer yang menunggu approval
    pending_developers = User.query.filter_by(role='developer', is_approved=False).all()
    approved_developers = User.query.filter_by(role='developer', is_approved=True).all()
    
    return render_template('admin/developer_requests.html',
                         pending_developers=pending_developers,
                         approved_developers=approved_developers)

@app.route('/admin/developer/approve/<int:developer_id>', methods=['POST'])
@login_required
def admin_approve_developer(developer_id):
    """Admin menyetujui developer"""
    if current_user.role != 'admin':
        flash('Akses ditolak', 'error')
        return redirect(url_for('index'))
    
    developer = User.query.get_or_404(developer_id)
    
    if developer.role != 'developer':
        flash('User ini bukan developer', 'error')
        return redirect(url_for('admin_developer_requests'))
    
    # Generate temporary password
    temp_password = str(uuid.uuid4())[:8]
    developer.set_password(temp_password)
    developer.is_temp_password = True  # Mark sebagai temp password
    developer.approve_developer()
    db.session.commit()
    
    # Kirim email approval dengan credentials
    send_developer_approval_email(developer, temp_password)
    
    flash(f'Developer {developer.username} telah disetujui! Email konfirmasi telah dikirim.', 'success')
    return redirect(url_for('admin_developer_requests'))

@app.route('/admin/developer/reject/<int:developer_id>', methods=['POST'])
@login_required
def admin_reject_developer(developer_id):
    """Admin menolak developer"""
    if current_user.role != 'admin':
        flash('Akses ditolak', 'error')
        return redirect(url_for('index'))
    
    developer = User.query.get_or_404(developer_id)
    
    if developer.role != 'developer':
        flash('User ini bukan developer', 'error')
        return redirect(url_for('admin_developer_requests'))
    
    username = developer.username
    developer.reject_developer()
    db.session.commit()
    
    # TODO: Kirim email penolakan ke developer
    
    flash(f'Developer {username} telah ditolak.', 'success')
    return redirect(url_for('admin_developer_requests'))

# ==================== ADMIN ACCOUNT MANAGEMENT ====================

@app.route('/admin/account-deletion-requests')
@login_required
def admin_account_deletion_requests():
    """Admin lihat permohonan penghapusan akun"""
    if current_user.role != 'admin':
        flash('Akses ditolak', 'error')
        return redirect(url_for('index'))
    
    # Ambil user yang minta penghapusan (menunggu persetujuan)
    pending_requests = User.query.filter_by(delete_requested=True).order_by(User.delete_requested_at.desc()).all()
    
    # Untuk now, completed_requests kosong karena user dihapus saat diapprove
    # Di masa depan bisa ditambah deletion_status field untuk tracking yang lebih baik
    completed_requests = []
    
    return render_template('admin/account_deletion_requests.html', 
                         pending_requests=pending_requests,
                         completed_requests=completed_requests)

@app.route('/admin/account/approve-delete/<int:user_id>', methods=['POST'])
@login_required
def admin_approve_account_deletion(user_id):
    """Admin approve penghapusan akun"""
    if current_user.role != 'admin':
        flash('Akses ditolak', 'error')
        return redirect(url_for('index'))
    
    user = User.query.get_or_404(user_id)
    
    if not user.delete_requested:
        flash('User ini tidak memiliki permohonan penghapusan akun', 'error')
        return redirect(url_for('admin_account_deletion_requests'))
    
    # Kirim email konfirmasi
    send_account_deletion_approved_email(user)
    
    username = user.username
    
    # Hapus semua data user (aplikasi, review, dll)
    if user.role == 'developer':
        # Hapus aplikasi dan folder mereka
        apps = App.query.filter_by(user_id=user.id).all()
        for app_item in apps:
            folder_name = None
            if app_item.icon:
                folder_name = app_item.icon.split('/')[0]
            elif app_item.file_path:
                folder_name = app_item.file_path.split('/')[0]
            
            if folder_name:
                folder_path = os.path.join(current_app.config['UPLOAD_FOLDER'], folder_name)
                if os.path.exists(folder_path):
                    shutil.rmtree(folder_path)
            
            db.session.delete(app_item)
    
    # Hapus review user
    Review.query.filter_by(user_id=user.id).delete()
    
    # Hapus user
    db.session.delete(user)
    db.session.commit()
    
    flash(f'✅ Akun {username} telah dihapus permanen. Email konfirmasi telah dikirim.', 'success')
    return redirect(url_for('admin_account_deletion_requests'))

@app.route('/admin/account/reject-delete/<int:user_id>', methods=['POST'])
@login_required
def admin_reject_account_deletion(user_id):
    """Admin tolak permohonan penghapusan akun"""
    if current_user.role != 'admin':
        flash('Akses ditolak', 'error')
        return redirect(url_for('index'))
    
    user = User.query.get_or_404(user_id)
    
    if not user.delete_requested:
        flash('User ini tidak memiliki permohonan penghapusan akun', 'error')
        return redirect(url_for('admin_account_deletion_requests'))
    
    # Kirim email penolakan
    send_account_deletion_rejected_email(user)
    
    # Reset flag penghapusan
    user.delete_requested = False
    user.delete_requested_at = None
    db.session.commit()
    
    flash(f'✅ Permohonan penghapusan {user.username} telah ditolak. Email notifikasi telah dikirim.', 'success')
    return redirect(url_for('admin_account_deletion_requests'))

# ==================== ADMIN REVIEWS ROUTES ====================

@app.route('/admin/reviews')
@login_required
def admin_reviews():
    """Halaman kelola semua review"""
    if current_user.role != 'admin':
        flash('Akses ditolak', 'error')
        return redirect(url_for('index'))
    
    # Ambil semua review dengan informasi app dan user
    reviews = Review.query.order_by(Review.created_at.desc()).all()
    return render_template('admin/reviews.html', reviews=reviews)

@app.route('/admin/reply/<int:review_id>', methods=['POST'])
@login_required
def admin_reply_review(review_id):
    """Admin membalas review user"""
    if current_user.role != 'admin':
        flash('Akses ditolak', 'error')
        return redirect(url_for('index'))
    
    review = Review.query.get_or_404(review_id)
    reply = request.form.get('reply', '').strip()
    
    if not reply:
        flash('Balasan tidak boleh kosong', 'error')
        return redirect(url_for('app_detail', app_id=review.app_id))
    
    review.admin_reply = reply
    review.admin_reply_at = datetime.utcnow()
    db.session.commit()


@app.route('/admin/review/edit/<int:review_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_review(review_id):
    if current_user.role != 'admin':
        flash('Akses ditolak', 'error')
        return redirect(url_for('index'))
    review = Review.query.get_or_404(review_id)
    if request.method == 'POST':
        try:
            rating = int(request.form.get('rating', review.rating))
        except:
            rating = review.rating
        comment = request.form.get('comment', review.comment)
        admin_reply = request.form.get('admin_reply', review.admin_reply)

        review.rating = max(1, min(5, rating))
        review.comment = comment
        # Admin reply handling
        if admin_reply and admin_reply.strip():
            review.admin_reply = admin_reply.strip()
            review.admin_reply_at = datetime.utcnow()

        db.session.commit()
        flash('Review berhasil diperbarui', 'success')
        return redirect(url_for('admin_reviews'))

    return render_template('admin/edit_review.html', review=review)


@app.route('/admin/review/location/<int:review_id>')
@login_required
def admin_review_location(review_id):
    if current_user.role != 'admin':
        flash('Akses ditolak', 'error')
        return redirect(url_for('index'))
    review = Review.query.get_or_404(review_id)
    # If no destination stored, redirect back to the review list and jump to the review card
    if not review.destination_location:
        flash('Tidak ada lokasi tersimpan untuk review ini. Mengarahkan ke daftar review.', 'info')
        return redirect(url_for('admin_reviews') + f"#review-{review.id}")
    return render_template('admin/view_location.html', location=review.destination_location, back='review', obj_id=review.id)


@app.route('/admin/review/delete/<int:review_id>', methods=['POST'])
@login_required
def admin_delete_review(review_id):
    if current_user.role != 'admin':
        flash('Akses ditolak', 'error')
        return redirect(url_for('index'))
    review = Review.query.get_or_404(review_id)
    db.session.delete(review)
    db.session.commit()
    flash('Review berhasil dihapus', 'success')
    return redirect(url_for('admin_reviews'))
    
    flash('Balasan berhasil dikirim!', 'success')
    return redirect(url_for('app_detail', app_id=review.app_id))

@app.route('/admin/reply/delete/<int:review_id>')
@login_required
def admin_delete_reply(review_id):
    """Admin menghapus balasan"""
    if current_user.role != 'admin':
        flash('Akses ditolak', 'error')
        return redirect(url_for('index'))
    
    review = Review.query.get_or_404(review_id)
    app_id = review.app_id
    review.admin_reply = None
    review.admin_reply_at = None
    db.session.commit()
    
    flash('Balasan berhasil dihapus', 'success')
    return redirect(url_for('app_detail', app_id=app_id))

# ==================== ADMIN HELP REQUESTS ROUTES ====================

@app.route('/admin/help-requests')
@login_required
def admin_help_requests():
    """Admin melihat semua permohonan bantuan"""
    if current_user.role != 'admin':
        flash('Akses ditolak', 'error')
        return redirect(url_for('index'))
    
    # Ambil semua help requests dengan status terbaru
    help_requests = HelpRequest.query.order_by(HelpRequest.created_at.desc()).all()
    
    # Hitung statistik
    total_requests = len(help_requests)
    pending_requests = len([h for h in help_requests if h.status == 'pending'])
    in_progress_requests = len([h for h in help_requests if h.status == 'in_progress'])
    resolved_requests = len([h for h in help_requests if h.status == 'resolved'])
    closed_requests = len([h for h in help_requests if h.status == 'closed'])
    
    return render_template('admin/help_requests.html',
                         help_requests=help_requests,
                         total_requests=total_requests,
                         pending_requests=pending_requests,
                         in_progress_requests=in_progress_requests,
                         resolved_requests=resolved_requests,
                         closed_requests=closed_requests)

@app.route('/admin/help-request/<int:request_id>')
@login_required
def admin_help_request_detail(request_id):
    """Admin melihat detail permohonan bantuan"""
    if current_user.role != 'admin':
        flash('Akses ditolak', 'error')
        return redirect(url_for('index'))
    
    help_request = HelpRequest.query.get_or_404(request_id)
    return render_template('admin/help_request_detail.html', help_request=help_request)

@app.route('/admin/help-request/<int:request_id>/update-status', methods=['POST'])
@login_required
def admin_update_help_request_status(request_id):
    """Admin update status permohonan bantuan"""
    if current_user.role != 'admin':
        flash('Akses ditolak', 'error')
        return redirect(url_for('index'))
    
    help_request = HelpRequest.query.get_or_404(request_id)
    new_status = request.form.get('status')
    admin_response = request.form.get('admin_response', '').strip()
    
    # Validasi status
    valid_statuses = ['pending', 'in_progress', 'resolved', 'closed']
    if new_status not in valid_statuses:
        flash('Status tidak valid', 'error')
        return redirect(url_for('admin_help_request_detail', request_id=request_id))
    
    # Update status
    help_request.status = new_status
    
    # Jika ada balasan admin, simpan dan kirim email
    if admin_response:
        help_request.admin_response = admin_response
        help_request.response_at = datetime.utcnow()
        
        # Kirim email notifikasi ke user
        email_sent = send_help_request_response_email(help_request)
        
        if email_sent:
            flash(f'✅ Status berhasil diupdate ke {new_status}! Email notifikasi telah dikirim ke {help_request.email}', 'success')
        else:
            flash(f'⚠️ Status berhasil diupdate ke {new_status}, tetapi gagal mengirim email. Silakan hubungi user secara langsung.', 'warning')
    else:
        db.session.commit()
        flash(f'Status berhasil diupdate ke {new_status}', 'success')
    
    return redirect(url_for('admin_help_request_detail', request_id=request_id))

@app.route('/admin/help-request/<int:request_id>/delete', methods=['POST'])
@login_required
def admin_delete_help_request(request_id):
    """Admin menghapus permohonan bantuan"""
    if current_user.role != 'admin':
        flash('Akses ditolak', 'error')
        return redirect(url_for('index'))
    
    help_request = HelpRequest.query.get_or_404(request_id)
    help_request_id = help_request.id
    db.session.delete(help_request)
    db.session.commit()
    
    flash('Permohonan bantuan berhasil dihapus', 'success')
    return redirect(url_for('admin_help_requests'))

# ==================== DEVELOPER ROUTES ====================


@app.route('/developer/dashboard')
@login_required
def developer_dashboard():
    """Halaman dashboard utama untuk developer"""
    if current_user.role != 'developer':
        flash('Akses hanya untuk developer', 'error')
        return redirect(url_for('index'))
    
    if not current_user.is_approved:
        flash('Akun developer Anda belum disetujui oleh admin', 'warning')
        return redirect(url_for('index'))
    
    # Ambil semua aplikasi milik developer ini
    my_apps = App.query.filter_by(user_id=current_user.id).all()
    
    # Total downloads dari semua aplikasi
    total_downloads = sum(app.downloads for app in my_apps)
    
    # Total followers
    follower_count = UserFollowDeveloper.query.filter_by(developer_id=current_user.id).count()
    
    # Total reviews dari semua aplikasi
    total_reviews = 0
    for app in my_apps:
        total_reviews += len(app.reviews)
    
    return render_template('developer/dashboard.html',
                         my_apps=my_apps,
                         total_downloads=total_downloads,
                         follower_count=follower_count,
                         total_reviews=total_reviews)


@app.route('/developer/apps')
@login_required
def developer_apps():
    """Halaman daftar aplikasi milik developer"""
    if current_user.role != 'developer':
        flash('Akses hanya untuk developer', 'error')
        return redirect(url_for('index'))
    
    if not current_user.is_approved:
        flash('Akun developer Anda belum disetujui oleh admin', 'warning')
        return redirect(url_for('index'))
    
    # Ambil aplikasi milik developer ini
    apps = App.query.filter_by(user_id=current_user.id).order_by(App.created_at.desc()).all()
    
    return render_template('developer/apps.html', apps=apps)

@app.route('/developer/apps/add', methods=['GET', 'POST'])
@login_required
def developer_app_add():
    """Developer upload aplikasi baru"""
    if current_user.role != 'developer':
        flash('Akses hanya untuk developer', 'error')
        return redirect(url_for('index'))
    
    if not current_user.is_approved:
        flash('Akun developer Anda belum disetujui oleh admin', 'warning')
        return redirect(url_for('index'))
    
    categories = Category.query.all()
    
    if request.method == 'POST':
        try:
            title = request.form.get('title')
            
            if not title:
                flash("Judul aplikasi wajib diisi!", "danger")
                return render_template('developer/app_form.html', categories=categories)
            
            description = request.form.get('description')
            category_id = request.form.get('category_id')
            category_id = int(category_id) if category_id else None
            version = request.form.get('version')
            size = request.form.get('size')
            price = request.form.get('price', 'Gratis')
            
            # Buat app baru
            app_new = App(
                title=title,
                description=description,
                category_id=category_id,
                version=version,
                size=size,
                price=price,
                developer=current_user.username,  # Set developer dari user login
                user_id=current_user.id,  # Set user_id untuk tracking
                rating=0.0,
                is_active=True  # Developer app langsung aktif
            )
            db.session.add(app_new)
            db.session.commit()
            
            # Buat folder
            app_slug, icon_folder, file_folder, screenshots_folder = create_app_folders(app_new.title, app_new.id)
            
            # Upload icon
            icon_file = request.files.get('icon')
            icon_filename = None
            if icon_file and icon_file.filename and allowed_file(icon_file.filename):
                filename = f"{uuid.uuid4().hex}_{secure_filename(icon_file.filename)}"
                icon_file.save(os.path.join(icon_folder, filename))
                icon_filename = f"{app_slug}/icon/{filename}"
            
            # Upload file aplikasi
            file_upload = request.files.get('file_path')
            file_filename = None
            if file_upload and file_upload.filename and allowed_file(file_upload.filename):
                filename = f"{uuid.uuid4().hex}_{secure_filename(file_upload.filename)}"
                file_upload.save(os.path.join(file_folder, filename))
                file_filename = f"{app_slug}/file/{filename}"
            
            # Upload screenshots
            screenshot_files = request.files.getlist('screenshots')
            screenshot_names = []
            for file in screenshot_files:
                if file and file.filename and allowed_file(file.filename):
                    filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
                    file.save(os.path.join(screenshots_folder, filename))
                    screenshot_names.append(f"{app_slug}/screenshots/{filename}")
            
            screenshots_string = ",".join(screenshot_names) if screenshot_names else None
            
            # Update database dengan path file
            app_new.icon = icon_filename
            app_new.file_path = file_filename
            app_new.screenshots = screenshots_string
            db.session.commit()
            
            # Track upload in history
            upload_record = AppUpload(
                app_id=app_new.id,
                developer_id=current_user.id,
                version=version,
                notes="Aplikasi baru"
            )
            db.session.add(upload_record)
            db.session.commit()
            
            # Notify followers about new app
            followers = UserFollowDeveloper.query.filter_by(developer_id=current_user.id).all()
            for follow in followers:
                notification = Notification(
                    user_id=follow.user_id,
                    app_id=app_new.id,
                    message=f"{current_user.username} telah meluncurkan aplikasi baru: {app_new.title}",
                    notification_type='new_app'
                )
                db.session.add(notification)
            db.session.commit()
            
            flash("✅ Aplikasi berhasil diunggah! Aplikasi Anda sekarang bisa diunduh oleh pengguna.", "success")
            return redirect(url_for('developer_apps'))
            
        except Exception as e:
            db.session.rollback()
            flash(f"Terjadi kesalahan: {str(e)}", "danger")
    
    return render_template('developer/app_form.html', categories=categories)

@app.route('/developer/apps/edit/<int:app_id>', methods=['GET', 'POST'])
@login_required
def developer_app_edit(app_id):
    """Developer edit aplikasi miliknya"""
    if current_user.role != 'developer':
        flash('Akses hanya untuk developer', 'error')
        return redirect(url_for('index'))
    
    if not current_user.is_approved:
        flash('Akun developer Anda belum disetujui oleh admin', 'warning')
        return redirect(url_for('index'))
    
    app_edit = App.query.get_or_404(app_id)
    
    # Cek kepemilikan
    if app_edit.user_id != current_user.id:
        flash('Anda tidak memiliki izin untuk mengubah aplikasi ini', 'error')
        return redirect(url_for('developer_apps'))
    
    categories = Category.query.all()
    
    if request.method == 'POST':
        try:
            title = request.form.get('title')
            
            if not title:
                flash("Judul aplikasi wajib diisi!", "danger")
                return render_template('developer/app_form.html', app=app_edit, categories=categories)
            
            app_edit.title = title
            app_edit.description = request.form.get('description')
            category_id = request.form.get('category_id')
            app_edit.category_id = int(category_id) if category_id else None
            app_edit.version = request.form.get('version')
            app_edit.size = request.form.get('size')
            app_edit.price = request.form.get('price', 'Gratis')
            
            # Logic untuk rename folder jika title berubah
            old_folder_name = None
            if app_edit.icon:
                old_folder_name = app_edit.icon.split('/')[0]
            elif app_edit.file_path:
                old_folder_name = app_edit.file_path.split('/')[0]
            elif app_edit.screenshots:
                old_folder_name = app_edit.screenshots.split(',')[0].split('/')[0]
            
            new_slug = slugify(title)
            if not new_slug: 
                new_slug = "untitled"
            new_folder_name = f"{app_edit.id}-{new_slug}"
            
            if old_folder_name and old_folder_name != new_folder_name:
                old_path = os.path.join(app.config['UPLOAD_FOLDER'], old_folder_name)
                new_path = os.path.join(app.config['UPLOAD_FOLDER'], new_folder_name)
                
                if os.path.exists(old_path):
                    os.rename(old_path, new_path)
                    
                    if app_edit.icon:
                        app_edit.icon = app_edit.icon.replace(old_folder_name, new_folder_name, 1)
                    if app_edit.file_path:
                        app_edit.file_path = app_edit.file_path.replace(old_folder_name, new_folder_name, 1)
                    if app_edit.screenshots:
                        app_edit.screenshots = app_edit.screenshots.replace(old_folder_name, new_folder_name)
            
            # Set path folder
            base_folder = os.path.join(app.config['UPLOAD_FOLDER'], new_folder_name)
            icon_folder = os.path.join(base_folder, "icon")
            file_folder = os.path.join(base_folder, "file")
            screenshots_folder = os.path.join(base_folder, "screenshots")
            
            os.makedirs(icon_folder, exist_ok=True)
            os.makedirs(file_folder, exist_ok=True)
            os.makedirs(screenshots_folder, exist_ok=True)
            
            # Update icon
            icon_file = request.files.get('icon')
            if icon_file and icon_file.filename and allowed_file(icon_file.filename):
                if app_edit.icon:
                    old_path = os.path.join(app.config['UPLOAD_FOLDER'], app_edit.icon)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                
                filename = f"{uuid.uuid4().hex}_{secure_filename(icon_file.filename)}"
                icon_file.save(os.path.join(icon_folder, filename))
                app_edit.icon = f"{new_folder_name}/icon/{filename}"
            
            # Update file
            file_upload = request.files.get('file_path')
            if file_upload and file_upload.filename and allowed_file(file_upload.filename):
                if app_edit.file_path:
                    old_path = os.path.join(app.config['UPLOAD_FOLDER'], app_edit.file_path)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                
                filename = f"{uuid.uuid4().hex}_{secure_filename(file_upload.filename)}"
                file_upload.save(os.path.join(file_folder, filename))
                app_edit.file_path = f"{new_folder_name}/file/{filename}"
            
            # Update screenshots
            screenshot_files = request.files.getlist('screenshots')
            new_screenshots = []
            
            for file in screenshot_files:
                if file and file.filename and allowed_file(file.filename):
                    filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
                    file.save(os.path.join(screenshots_folder, filename))
                    new_screenshots.append(f"{new_folder_name}/screenshots/{filename}")
            
            if new_screenshots:
                existing = app_edit.screenshots.split(',') if app_edit.screenshots else []
                existing = [s.replace(old_folder_name, new_folder_name) for s in existing] if old_folder_name else existing
                app_edit.screenshots = ",".join(existing + new_screenshots)
            
            db.session.commit()
            
            # Track update in history
            new_version = request.form.get('version')
            update_notes = request.form.get('update_notes', 'Update aplikasi')
            upload_record = AppUpload(
                app_id=app_id,
                developer_id=current_user.id,
                version=new_version,
                notes=update_notes
            )
            db.session.add(upload_record)
            db.session.commit()
            
            # Notify followers about update
            followers = UserFollowDeveloper.query.filter_by(developer_id=current_user.id).all()
            for follow in followers:
                notification = Notification(
                    user_id=follow.user_id,
                    app_id=app_id,
                    message=f"Aplikasi {app_edit.title} dari {current_user.username} telah diupdate ke versi {new_version}",
                    notification_type='app_update'
                )
                db.session.add(notification)
            db.session.commit()
            
            flash("✅ Aplikasi berhasil diperbarui!", "success")
            return redirect(url_for('developer_apps'))
            
        except Exception as e:
            db.session.rollback()
            flash(f"Terjadi kesalahan: {str(e)}", "danger")
    
    return render_template('developer/app_form.html', app=app_edit, categories=categories)

@app.route('/developer/apps/delete/<int:app_id>')
@login_required
def developer_app_delete(app_id):
    """Developer hapus aplikasi miliknya"""
    if current_user.role != 'developer':
        flash('Akses hanya untuk developer', 'error')
        return redirect(url_for('index'))
    
    app_del = App.query.get_or_404(app_id)
    
    # Cek kepemilikan
    if app_del.user_id != current_user.id:
        flash('Anda tidak memiliki izin untuk menghapus aplikasi ini', 'error')
        return redirect(url_for('developer_apps'))
    
    # Cari dan hapus folder
    folder_name = None
    if app_del.icon:
        folder_name = app_del.icon.split('/')[0]
    elif app_del.file_path:
        folder_name = app_del.file_path.split('/')[0]
    
    if folder_name:
        folder_path = os.path.join(app.config['UPLOAD_FOLDER'], folder_name)
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
    
    app_title = app_del.title
    db.session.delete(app_del)
    db.session.commit()
    
    flash(f'✅ Aplikasi "{app_title}" berhasil dihapus', 'success')
    return redirect(url_for('developer_apps'))


# ==================== FOLLOW DEVELOPER ROUTES ====================

@app.route('/follow-developer/<int:developer_id>', methods=['POST'])
@login_required
def follow_developer(developer_id):
    """User follow developer untuk mendapatkan notifikasi update"""
    if current_user.role == 'developer':
        flash('Developer tidak bisa follow developer lain', 'warning')
        return redirect(request.referrer or url_for('index'))
    
    developer = User.query.get_or_404(developer_id)
    if developer.role != 'developer':
        flash('User ini bukan developer', 'error')
        return redirect(request.referrer or url_for('index'))
    
    # Cek apakah sudah follow
    existing = UserFollowDeveloper.query.filter_by(
        user_id=current_user.id,
        developer_id=developer_id
    ).first()
    
    if existing:
        flash('Anda sudah mengikuti developer ini', 'info')
    else:
        follow = UserFollowDeveloper(
            user_id=current_user.id,
            developer_id=developer_id
        )
        db.session.add(follow)
        db.session.commit()
        flash(f'✅ Anda sekarang mengikuti {developer.username}', 'success')
    
    return redirect(request.referrer or url_for('index'))

@app.route('/unfollow-developer/<int:developer_id>', methods=['POST'])
@login_required
def unfollow_developer(developer_id):
    """User unfollow developer"""
    follow = UserFollowDeveloper.query.filter_by(
        user_id=current_user.id,
        developer_id=developer_id
    ).first_or_404()
    
    developer_name = follow.developer.username
    db.session.delete(follow)
    db.session.commit()
    flash(f'✅ Anda berhenti mengikuti {developer_name}', 'success')
    
    return redirect(request.referrer or url_for('index'))

# ==================== DEVELOPER HISTORY DASHBOARD ====================

@app.route('/developer/history')
@login_required
def developer_history():
    """Developer dashboard untuk melihat upload history dan download history"""
    if current_user.role != 'developer':
        flash('Akses hanya untuk developer', 'error')
        return redirect(url_for('index'))
    
    if not current_user.is_approved:
        flash('Akun developer Anda belum disetujui oleh admin', 'warning')
        return redirect(url_for('index'))
    
    # Upload history
    uploads = AppUpload.query.filter_by(developer_id=current_user.id).order_by(AppUpload.uploaded_at.desc()).all()
    
    # Download history dari apps milik developer
    developer_apps = App.query.filter_by(user_id=current_user.id).all()
    app_ids = [app.id for app in developer_apps]
    
    downloads = AppDownload.query.filter(AppDownload.app_id.in_(app_ids)).order_by(AppDownload.downloaded_at.desc()).all() if app_ids else []
    
    # Followers
    followers = UserFollowDeveloper.query.filter_by(developer_id=current_user.id).count()
    
    return render_template('developer/history.html', 
                         uploads=uploads,
                         downloads=downloads,
                         followers=followers,
                         developer_apps=developer_apps)

# ==================== USER HISTORY DASHBOARD ====================

@app.route('/user/history')
@login_required
def user_history():
    """User dashboard untuk melihat download history"""
    if current_user.role != 'user':
        flash('Akses hanya untuk user', 'error')
        return redirect(url_for('index'))
    
    # Get all downloads for this user, ordered by date
    all_downloads = AppDownload.query.filter_by(user_id=current_user.id).order_by(AppDownload.downloaded_at.desc()).all()
    
    # Filter to get only one record per app (the latest one)
    # This ensures we show unique apps in the library
    seen_apps = set()
    unique_downloads = []
    for download in all_downloads:
        if download.app_id not in seen_apps:
            seen_apps.add(download.app_id)
            unique_downloads.append(download)
    
    # Following developers
    following = UserFollowDeveloper.query.filter_by(user_id=current_user.id).all()
    
    # Count unique apps downloaded
    unique_app_count = len(unique_downloads)
    
    # Count available updates (where downloaded version differs from current app version)
    updates_available = 0
    for download in unique_downloads:
        if download.version != download.app.version:
            updates_available += 1
    
    # Get unread notifications count
    unread_notifications = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    
    return render_template('user/history.html', 
                         downloads=unique_downloads,
                         following=following,
                         unique_app_count=unique_app_count,
                         updates_available=updates_available,
                         unread_notifications=unread_notifications)

# ==================== NOTIFICATIONS ====================

@app.route('/notifications')
@login_required
def notifications():
    """Tampilkan semua notifikasi user"""
    notifications_list = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    unread_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    
    return render_template('notifications.html', 
                         notifications=notifications_list,
                         unread_count=unread_count)

@app.route('/notification/<int:notification_id>/read', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    """Mark notification as read"""
    notification = Notification.query.get_or_404(notification_id)
    
    if notification.user_id != current_user.id:
        return {'error': 'Unauthorized'}, 403
    
    notification.is_read = True
    db.session.commit()
    
    return {'success': True}

@app.route('/notifications/mark-all-read', methods=['POST'])
@login_required
def mark_all_notifications_read():
    """Mark all notifications as read"""
    Notification.query.filter_by(user_id=current_user.id, is_read=False).update({'is_read': True})
    db.session.commit()
    
    return {'success': True}

# ==================== MAINTENANCE MANAGEMENT ====================

def get_available_routes():
    """Dapatkan list semua routes yang tersedia untuk maintenance"""
    available_routes = [
        {'name': 'index', 'path': '/', 'description': 'Halaman Utama'},
        {'name': 'kategori', 'path': '/kategori', 'description': 'Kategori'},
        {'name': 'search', 'path': '/search', 'description': 'Pencarian'},
        {'name': 'developer_detail', 'path': '/developer/<int:developer_id>', 'description': 'Detail Developer'},
        {'name': 'app_detail', 'path': '/app/<int:app_id>', 'description': 'Detail Aplikasi'},
        {'name': 'login', 'path': '/login', 'description': 'Halaman Login'},
        {'name': 'register', 'path': '/register', 'description': 'Halaman Register'},
        {'name': 'profile', 'path': '/profile', 'description': 'Profil User'},
        {'name': 'admin_dashboard', 'path': '/admin', 'description': 'Dashboard Admin'},
        {'name': 'admin_apps', 'path': '/admin/apps', 'description': 'Kelola Aplikasi'},
        {'name': 'admin_users', 'path': '/admin/users', 'description': 'Kelola Pengguna'},
        {'name': 'admin_categories', 'path': '/admin/categories', 'description': 'Kelola Kategori'},
        {'name': 'developer_dashboard', 'path': '/developer', 'description': 'Dashboard Developer'},
    ]
    return available_routes

def init_maintenance_routes():
    """Initialize default maintenance routes jika belum ada"""
    available_routes = get_available_routes()
    for route in available_routes:
        if not MaintenanceRoute.query.filter_by(route_name=route['name']).first():
            new_route = MaintenanceRoute(
                route_name=route['name'],
                route_path=route['path'],
                is_maintenance=False
            )
            db.session.add(new_route)
    db.session.commit()

@app.route('/admin/maintenance')
@login_required
def admin_maintenance():
    """Admin dashboard untuk manage maintenance routes"""
    if current_user.role != 'admin':
        flash('Akses ditolak', 'error')
        return redirect(url_for('index'))
    
    # Initialize default routes jika belum ada
    init_maintenance_routes()
    
    maintenance_routes = MaintenanceRoute.query.order_by(MaintenanceRoute.route_name).all()
    
    return render_template('admin/maintenance.html', maintenance_routes=maintenance_routes)

@app.route('/api/maintenance/routes', methods=['GET'])
@login_required
def api_get_maintenance_routes():
    """Get all maintenance routes"""
    if current_user.role != 'admin':
        return {'error': 'Unauthorized'}, 403
    
    routes = MaintenanceRoute.query.order_by(MaintenanceRoute.route_name).all()
    routes_data = []
    for route in routes:
        routes_data.append({
            'id': route.id,
            'name': route.route_name,
            'path': route.route_path,
            'is_maintenance': route.is_maintenance,
            'message': route.maintenance_message
        })
    
    return {'routes': routes_data}

@app.route('/api/maintenance/toggle', methods=['POST'])
@login_required
def api_toggle_maintenance():
    """Toggle maintenance status untuk route tertentu"""
    if current_user.role != 'admin':
        return {'error': 'Unauthorized'}, 403
    
    data = request.get_json()
    route_id = data.get('route_id')
    is_maintenance = data.get('is_maintenance')
    maintenance_message = data.get('message', 'Platform sedang dalam pemeliharaan. Mohon menunggu.')
    
    if not route_id:
        return {'error': 'route_id tidak ditemukan'}, 400
    
    route = MaintenanceRoute.query.get_or_404(route_id)
    route.is_maintenance = is_maintenance
    route.maintenance_message = maintenance_message
    route.updated_at = datetime.utcnow()
    db.session.commit()
    
    return {
        'success': True,
        'route': {
            'id': route.id,
            'name': route.route_name,
            'is_maintenance': route.is_maintenance,
            'message': route.maintenance_message
        }
    }

# ==================== MIDDLEWARE & DECORATORS ====================

@app.before_request
def check_maintenance():
    """Check apakah route yang diakses sedang maintenance"""
    try:
        # Admin tidak perlu maintenance check
        if current_user.is_authenticated and current_user.role == 'admin':
            return None
        
        # Get current endpoint
        endpoint = request.endpoint
        if not endpoint:
            return None
        
        # Skip maintenance check untuk routes tertentu
        skip_routes = ['static', 'api_get_maintenance_routes', 'api_toggle_maintenance', 
                       'maintenance_page', 'logout', 'admin_maintenance', 'admin_temp_login']
        if endpoint in skip_routes:
            return None
        
        # Map endpoint ke route_name
        endpoint_to_route_name = {
            'index': 'index',
            'seluruh_kategori': 'kategori',
            'search': 'search',
            'developer_detail': 'developer_detail',
            'app_detail': 'app_detail',
            'profile': 'profile',
            'admin_dashboard': 'admin_dashboard',
            'admin_apps': 'admin_apps',
            'admin_users': 'admin_users',
            'admin_categories': 'admin_categories',
            'developer_dashboard': 'developer_dashboard',
            'login': 'login',
            'register': 'register',
        }
        
        route_name = endpoint_to_route_name.get(endpoint)
        if not route_name:
            return None
        
        # Check apakah route sedang maintenance
        maintenance_route = MaintenanceRoute.query.filter_by(route_name=route_name, is_maintenance=True).first()
        if maintenance_route:
            # Jika login sedang maintenance, skip redirect ke sebelum login page (sudah auto redirect)
            if route_name == 'login':
                return None
            return redirect(url_for('maintenance_page', route_name=route_name))
        
        return None
    except Exception as e:
        # Jika error (misal table tidak exist), skip maintenance check
        print(f"Maintenance check error: {str(e)}")
        return None

@app.route('/maintenance')
def maintenance_page():
    """Halaman maintenance"""
    route_name = request.args.get('route_name', 'unknown')
    maintenance_route = MaintenanceRoute.query.filter_by(route_name=route_name).first()
    message = maintenance_route.maintenance_message if maintenance_route else 'Platform sedang dalam pemeliharaan. Mohon menunggu.'
    
    # Check if login is under maintenance
    login_maintenance = MaintenanceRoute.query.filter_by(route_name='login', is_maintenance=True).first()
    
    return render_template('maintenance.html', message=message, route_name=route_name, 
                         login_maintenance=login_maintenance, current_route_name=route_name)

@app.errorhandler(404)
def error_404(e):
    return render_template('error.html', code=404, message='Halaman tidak ditemukan'), 404

@app.errorhandler(500)
def error_500(e):
    return render_template('error.html', code=500, message='Terjadi kesalahan server'), 500

# ==================== MAIN ====================
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
