-- ============================================================
-- Comic Book Management System with POS
-- Database Schema for MySQL (XAMPP / phpMyAdmin)
-- ============================================================

-- Create the database
CREATE DATABASE IF NOT EXISTS comic_book_db;
USE comic_book_db;

-- ============================================================
-- USERS TABLE
-- Stores admin and staff accounts
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    role ENUM('Admin', 'Staff') NOT NULL DEFAULT 'Staff',
    email VARCHAR(100) DEFAULT '',
    security_question VARCHAR(200) DEFAULT '',
    security_answer VARCHAR(200) DEFAULT '',
    security_question_1 VARCHAR(200) DEFAULT '',
    security_answer_1 VARCHAR(255) DEFAULT '',
    security_question_2 VARCHAR(200) DEFAULT '',
    security_answer_2 VARCHAR(255) DEFAULT '',
    security_question_3 VARCHAR(200) DEFAULT '',
    security_answer_3 VARCHAR(255) DEFAULT '',
    borrow_limit INT NOT NULL DEFAULT 5,
    is_archived TINYINT NOT NULL DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ============================================================
-- COMICS TABLE
-- Stores comic book inventory
-- ============================================================
CREATE TABLE IF NOT EXISTS comics (
    comic_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    author VARCHAR(100) NOT NULL,
    issue_number VARCHAR(20) DEFAULT '',
    publisher VARCHAR(100) DEFAULT '',
    category VARCHAR(50) DEFAULT '',
    price DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    stock_quantity INT NOT NULL DEFAULT 0,
    chapters INT NOT NULL DEFAULT 1,
    cover_image VARCHAR(255) DEFAULT '',
    synopsis TEXT,
    availability_status ENUM('Available', 'Out of Stock') DEFAULT 'Available',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ============================================================
-- SALES TABLE
-- Stores each sale transaction (header)
-- ============================================================
CREATE TABLE IF NOT EXISTS sales (
    sale_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    sale_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
) ENGINE=InnoDB;

-- ============================================================
-- SALE ITEMS TABLE
-- Stores each item in a sale (detail lines)
-- ============================================================
CREATE TABLE IF NOT EXISTS sale_items (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    sale_id INT NOT NULL,
    comic_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    unit_price DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    subtotal DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    FOREIGN KEY (sale_id) REFERENCES sales(sale_id),
    FOREIGN KEY (comic_id) REFERENCES comics(comic_id)
) ENGINE=InnoDB;

-- ============================================================
-- BORROW RECORDS TABLE
-- Stores borrow and return transactions
-- ============================================================
CREATE TABLE IF NOT EXISTS borrow_records (
    borrow_id INT AUTO_INCREMENT PRIMARY KEY,
    comic_id INT NOT NULL,
    borrower_name VARCHAR(100) NOT NULL,
    borrow_date DATE NOT NULL,
    due_date DATE DEFAULT NULL,
    return_date DATE DEFAULT NULL,
    status ENUM('Borrowed', 'Returned') DEFAULT 'Borrowed',
    condition_on_return ENUM('Good', 'Damaged', 'Lost') DEFAULT NULL,
    damage_notes TEXT,
    damage_fee DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    archive_status ENUM('Active', 'Archived') NOT NULL DEFAULT 'Active',
    user_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (comic_id) REFERENCES comics(comic_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
) ENGINE=InnoDB;

-- ============================================================
-- LOGIN LOGS TABLE
-- Tracks login times for admins and staff
-- ============================================================
CREATE TABLE IF NOT EXISTS login_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    login_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
) ENGINE=InnoDB;

-- ============================================================
-- ARCHIVED USERS TABLE
-- Stores recently deleted user accounts for recovery
-- ============================================================
CREATE TABLE IF NOT EXISTS archived_users (
    archive_id INT AUTO_INCREMENT PRIMARY KEY,
    original_user_id INT,
    username VARCHAR(50),
    password VARCHAR(255),
    full_name VARCHAR(100),
    email VARCHAR(100) DEFAULT '',
    role ENUM('Admin', 'Staff'),
    archived_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    archived_by INT,
    FOREIGN KEY (archived_by) REFERENCES users(user_id)
) ENGINE=InnoDB;

-- ============================================================
-- REFUNDS TABLE
-- Stores refund transactions for returned goods
-- ============================================================
CREATE TABLE IF NOT EXISTS refunds (
    refund_id INT AUTO_INCREMENT PRIMARY KEY,
    sale_id INT DEFAULT NULL,
    comic_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    refund_amount DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    reason TEXT,
    condition_status ENUM('Good', 'Damaged', 'Lost') DEFAULT 'Good',
    refunded_by INT NOT NULL,
    refund_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sale_id) REFERENCES sales(sale_id),
    FOREIGN KEY (comic_id) REFERENCES comics(comic_id),
    FOREIGN KEY (refunded_by) REFERENCES users(user_id)
) ENGINE=InnoDB;

-- ============================================================
-- DEFAULT ADMIN ACCOUNT
-- Username: admin  |  Password: admin123
-- ============================================================
INSERT INTO users (
    username, password, full_name, role,
    security_question, security_answer,
    security_question_1, security_answer_1,
    security_question_2, security_answer_2,
    security_question_3, security_answer_3,
    borrow_limit
)
VALUES (
    'admin', 'admin123', 'System Administrator', 'Admin',
    'What is your favorite color?', 'blue',
    'What is your favorite color?', 'blue',
    'What city were you born in?', 'manila',
    '', '',
    10
);

-- ============================================================
-- SAMPLE COMICS DATA
-- ============================================================
INSERT INTO comics (title, author, issue_number, publisher, category, price, stock_quantity, chapters, synopsis, availability_status) VALUES
('Spider-Man: Amazing Fantasy',  'Stan Lee',        '#15',  'Marvel',   'Superhero',   150.00,  20, 1, 'The origin story of Spider-Man, where Peter Parker gains his powers.', 'Available'),
('Batman: The Dark Knight',      'Frank Miller',    '#1',   'DC Comics','Superhero',   250.00,  15, 4, 'Batman returns from retirement to fight crime in a dystopian Gotham.', 'Available'),
('One Piece',                    'Eiichiro Oda',    '#1',   'Shueisha', 'Manga',       120.00,  30, 12, 'Monkey D. Luffy sets sail to find the legendary One Piece treasure.', 'Available'),
('Naruto',                       'Masashi Kishimoto','#1',  'Shueisha', 'Manga',       100.00,  25, 10, 'A young ninja seeks recognition and dreams of becoming the Hokage.', 'Available'),
('X-Men: First Class',           'Jeff Parker',     '#1',   'Marvel',   'Superhero',   180.00,   3, 6, 'The original X-Men team assembles under Professor Xavier.', 'Available'),
('Wonder Woman',                 'George Perez',    '#1',   'DC Comics','Superhero',   200.00,   4, 5, 'Diana of Themyscira enters the world of men as Wonder Woman.', 'Available'),
('Attack on Titan',              'Hajime Isayama',  '#1',   'Kodansha', 'Manga',       130.00,  18, 8, 'Humanity fights for survival against giant humanoid Titans.', 'Available'),
('The Walking Dead',             'Robert Kirkman',  '#1',   'Image',    'Horror',      175.00,  10, 6, 'Survivors navigate a world overrun by zombies.', 'Available'),
('Darna',                        'Mars Ravelo',     '#1',   'Pilipino Komiks','Filipino Hero', 80.00, 12, 3, 'A Filipina superhero who swallows a magical stone to gain powers.', 'Available'),
('Captain Barbell',              'Mars Ravelo',     '#1',   'Pilipino Komiks','Filipino Hero', 75.00,  2, 2, 'A skinny man transforms into a superhero by lifting a magical barbell.', 'Available');

-- ============================================================
-- SAMPLE STAFF ACCOUNT
-- Username: staff  |  Password: staff123
-- ============================================================
INSERT INTO users (
    username, password, full_name, role,
    security_question, security_answer,
    security_question_1, security_answer_1,
    security_question_2, security_answer_2,
    security_question_3, security_answer_3,
    borrow_limit
)
VALUES (
    'staff', 'staff123', 'Juan Dela Cruz', 'Staff',
    'What is your pet name?', 'buddy',
    'What is your pet name?', 'buddy',
    'What city were you born in?', 'cebu',
    '', '',
    5
);
