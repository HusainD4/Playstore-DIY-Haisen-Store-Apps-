-- ============================================================
-- QUERY SQL UNTUK ADMIN - MANAJEMEN HELP REQUESTS
-- Database: MySQL (XAMPP) - Port 3307
-- Database Name: haisen_db
-- ============================================================

-- ============================================================
-- 1. LIHAT SEMUA PERMOHONAN BANTUAN
-- ============================================================
SELECT
    hr.id,
    hr.name,
    hr.email,
    hr.issue_type,
    hr.issue_description,
    hr.message,
    hr.status,
    hr.admin_response,
    hr.response_at,
    hr.created_at
FROM help_requests hr
ORDER BY hr.created_at DESC;

-- ============================================================
-- 2. LIHAT PERMOHONAN BANTUAN DENGAN STATUS PENDING
-- ============================================================
SELECT
    hr.id,
    hr.name,
    hr.email,
    hr.issue_type,
    hr.issue_description,
    hr.message,
    hr.created_at
FROM help_requests hr
WHERE hr.status = 'pending'
ORDER BY hr.created_at ASC;

-- ============================================================
-- 3. LIHAT PERMOHONAN BANTUAN DENGAN STATUS IN_PROGRESS
-- ============================================================
SELECT
    hr.id,
    hr.name,
    hr.email,
    hr.issue_type,
    hr.issue_description,
    hr.message,
    hr.admin_response,
    hr.response_at,
    hr.created_at
FROM help_requests hr
WHERE hr.status = 'in_progress'
ORDER BY hr.created_at DESC;

-- ============================================================
-- 4. LIHAT PERMOHONAN BANTUAN YANG SUDAH DIRESOLUSI
-- ============================================================
SELECT
    hr.id,
    hr.name,
    hr.email,
    hr.issue_type,
    hr.issue_description,
    hr.message,
    hr.admin_response,
    hr.response_at,
    hr.created_at
FROM help_requests hr
WHERE hr.status = 'resolved'
ORDER BY hr.created_at DESC;

-- ============================================================
-- 5. STATISTIK PERMOHONAN BANTUAN
-- ============================================================
SELECT
    status,
    COUNT(*) as total,
    COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending,
    COUNT(CASE WHEN status = 'in_progress' THEN 1 END) as in_progress,
    COUNT(CASE WHEN status = 'resolved' THEN 1 END) as resolved,
    COUNT(CASE WHEN status = 'closed' THEN 1 END) as closed
FROM help_requests
GROUP BY status;

-- ============================================================
-- 6. STATISTIK PERMOHONAN BANTUAN PER JENIS MASALAH
-- ============================================================
SELECT
    issue_type,
    issue_description,
    COUNT(*) as total_requests,
    COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending,
    COUNT(CASE WHEN status = 'in_progress' THEN 1 END) as in_progress,
    COUNT(CASE WHEN status = 'resolved' THEN 1 END) as resolved
FROM help_requests
GROUP BY issue_type, issue_description
ORDER BY total_requests DESC;

-- ============================================================
-- 7. LIHAT PERMOHONAN BANTUAN TERBARU (10 TERAKHIR)
-- ============================================================
SELECT
    hr.id,
    hr.name,
    hr.email,
    hr.issue_type,
    hr.issue_description,
    hr.status,
    hr.created_at
FROM help_requests hr
ORDER BY hr.created_at DESC
LIMIT 10;

-- ============================================================
-- 8. LIHAT PERMOHONAN BANTUAN DALAM 7 HARI TERAKHIR
-- ============================================================
SELECT
    hr.id,
    hr.name,
    hr.email,
    hr.issue_type,
    hr.issue_description,
    hr.status,
    hr.created_at
FROM help_requests hr
WHERE hr.created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
ORDER BY hr.created_at DESC;

-- ============================================================
-- 9. UPDATE STATUS PERMOHONAN BANTUAN (PENDING -> IN_PROGRESS)
-- ============================================================
UPDATE help_requests
SET status = 'in_progress'
WHERE id = [ID_PERMOHONAN];

-- ============================================================
-- 10. UPDATE STATUS PERMOHONAN BANTUAN (IN_PROGRESS -> RESOLVED)
-- ============================================================
UPDATE help_requests
SET status = 'resolved',
    admin_response = '[BALASAN ADMIN]',
    response_at = NOW()
WHERE id = [ID_PERMOHONAN];

-- ============================================================
-- 11. UPDATE STATUS PERMOHONAN BANTUAN (RESOLVED -> CLOSED)
-- ============================================================
UPDATE help_requests
SET status = 'closed'
WHERE id = [ID_PERMOHONAN];

-- ============================================================
-- 12. UPDATE BALASAN ADMIN (Jika status masih pending/in_progress)
-- ============================================================
UPDATE help_requests
SET admin_response = '[BALASAN ADMIN]',
    response_at = NOW()
WHERE id = [ID_PERMOHONAN];

-- ============================================================
-- 13. HAPUS PERMOHONAN BANTUAN LAMA (LEWAT 90 HARI)
-- ============================================================
DELETE FROM help_requests
WHERE created_at < DATE_SUB(NOW(), INTERVAL 90 DAY);

-- ============================================================
-- 14. COUNT PERMOHONAN BANTUAN YANG BELUM DIRESOLUSI
-- ============================================================
SELECT COUNT(*) as unresolved_requests
FROM help_requests
WHERE status IN ('pending', 'in_progress');

-- ============================================================
-- 15. LIHAT PERMOHONAN BANTUAN BERDASARKAN EMAIL
-- ============================================================
SELECT
    hr.id,
    hr.name,
    hr.email,
    hr.issue_type,
    hr.issue_description,
    hr.message,
    hr.status,
    hr.admin_response,
    hr.response_at,
    hr.created_at
FROM help_requests hr
WHERE hr.email = '[EMAIL_USER]'
ORDER BY hr.created_at DESC;

-- ============================================================
-- 16. LIHAT PERMOHONAN BANTUAN BERDASARKAN NAMA
-- ============================================================
SELECT
    hr.id,
    hr.name,
    hr.email,
    hr.issue_type,
    hr.issue_description,
    hr.message,
    hr.status,
    hr.admin_response,
    hr.response_at,
    hr.created_at
FROM help_requests hr
WHERE hr.name LIKE '%[NAMA]%'
ORDER BY hr.created_at DESC;

-- ============================================================
-- 17. UPDATE STATUS BANYAK PERMOHONAN SEKALIGUS
-- ============================================================
UPDATE help_requests
SET status = 'in_progress'
WHERE status = 'pending'
AND created_at < DATE_SUB(NOW(), INTERVAL 24 HOUR);

-- ============================================================
-- 18. STATISTIK PERMOHONAN BANTUAN PER BULAN
-- ============================================================
SELECT
    DATE_FORMAT(created_at, '%Y-%m') as month,
    COUNT(*) as total_requests,
    COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending,
    COUNT(CASE WHEN status = 'in_progress' THEN 1 END) as in_progress,
    COUNT(CASE WHEN status = 'resolved' THEN 1 END) as resolved
FROM help_requests
GROUP BY DATE_FORMAT(created_at, '%Y-%m')
ORDER BY month DESC;

-- ============================================================
-- 19. LIHAT PERMOHONAN BANTUAN DENGAN BALASAN ADMIN
-- ============================================================
SELECT
    hr.id,
    hr.name,
    hr.email,
    hr.issue_type,
    hr.issue_description,
    hr.message,
    hr.admin_response,
    hr.response_at,
    hr.created_at
FROM help_requests hr
WHERE hr.admin_response IS NOT NULL
AND hr.admin_response != ''
ORDER BY hr.response_at DESC;

-- ============================================================
-- 20. RESET SEMUA STATUS KE PENDING (UNTUK TESTING)
-- ============================================================
UPDATE help_requests
SET status = 'pending',
    admin_response = NULL,
    response_at = NULL
WHERE status IN ('in_progress', 'resolved', 'closed');
