# Comic Book Management System with POS

A desktop application for managing a comic book store, built with **Python**, **PyQt6**, **MySQL**, and **Qt Charts**. It includes modules for inventory management, point of sale, borrow/return tracking, sales history, reports, and user management.

This system was developed as a school project using the **MVC (Model-View-Controller)** design pattern.

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Main Features and Modules](#main-features-and-modules)
3. [How the System Works](#how-the-system-works)
4. [Project Structure](#project-structure)
5. [Prerequisites](#prerequisites)
6. [Step-by-Step Installation Guide](#step-by-step-installation-guide)
7. [Configuration (config.py)](#configuration-configpy)
8. [Default Login Accounts](#default-login-accounts)
9. [User Roles and Permissions](#user-roles-and-permissions)
10. [Philippine Localization](#philippine-localization)
11. [Database Tables](#database-tables)
12. [Architecture (MVC Pattern)](#architecture-mvc-pattern)
13. [Troubleshooting](#troubleshooting)

---

## System Overview

The **Comic Book Management System with POS** is a desktop application designed for a small comic book store. It helps store staff and administrators manage their day-to-day operations in one place:

- **Track inventory** — keep a record of all comic books with title, author, publisher, price, and stock quantity.
- **Sell comics** — use the built-in Point of Sale (POS) to process sales, calculate totals, and generate receipts.
- **Borrow and return** — lend comics to borrowers and track when they are returned.
- **View sales history** — look up past transactions by date and see detailed breakdowns.
- **Generate reports** — view sales summaries, charts, and analytics (admin only).
- **Manage users** — create admin and staff accounts with different access levels (admin only).

The system uses **XAMPP MySQL** as its database and **PyQt6** for the graphical user interface (GUI). All dates and currency are displayed in **Philippine format**.

---

## Main Features and Modules

### 1. Dashboard

- Displays summary cards: Total Sales Today, Total Comics, Borrowed Count, Low Stock Count
- Four interactive charts: Daily Sales, Top Selling Comics, Stock Distribution (pie chart), Borrowed vs. Returned
- Recent transactions table showing the latest sales

### 2. Comics Inventory

- Add, edit, and delete comic book records
- Search/filter comics by title, author, or category
- Tracks: Title, Author, Issue Number, Publisher, Category, Price, Stock Quantity, Availability Status
- Rows with low stock are highlighted automatically

### 3. Point of Sale (POS)

- Select a comic from the dropdown and add it to the cart
- Adjust quantity and see the total update in real time
- Complete the sale and generate a printable receipt
- Stock is automatically reduced after each sale

### 4. Borrow / Return

- Borrow a comic — stock decreases by 1
- Return a comic — stock increases by 1
- Tracks borrower name, borrow date, return date, and status (Borrowed / Returned)
- Each record includes a timestamp showing when it was created

### 5. Sales History

- View all past transactions
- Filter by date range (start date and end date)
- See the total sales amount for the filtered period
- Double-click any row to view the full sale details (items, quantities, prices)

### 6. Reports (Admin Only)

- Generate sales reports for any date range
- Summary cards: Total Revenue, Number of Transactions, Average Sale Value
- Daily revenue bar chart for visual analysis

### 7. User Management (Admin Only)

- Add, edit, and delete system user accounts
- Assign roles: Admin or Staff
- Security setup uses 3 questions: Question 1 and Question 2 are required, Question 3 is optional
- Displays account creation date and time in Philippine format

### 8. Forgot Password Security

- Forgot Password requires answering both required security questions correctly
- If answers do not match, the system blocks reset and shows contact administrator guidance

---

## How the System Works

This section explains the basic flow of the system, which is useful for understanding during a project presentation or defense.

### Login Flow

1. The user opens the application and sees the **login screen**.
2. They enter their username and password.
3. The system checks the credentials against the `users` table in MySQL.
4. If valid, the **main window** opens with a sidebar showing the available modules based on the user's role.

### Selling a Comic (POS Flow)

1. The staff selects a comic from the dropdown.
2. They enter the quantity and click **Add to Cart**.
3. The cart table updates and the total is calculated automatically.
4. When ready, the staff clicks **Complete Sale**.
5. A **receipt** is generated and displayed.
6. The sale is saved in the `sales` and `sale_items` tables in the database.
7. The comic's stock quantity is reduced automatically.

### Borrowing and Returning

1. To borrow: select a comic, enter the borrower's name, and click **Borrow Product**. Borrow Date is set automatically to today and Due Date is auto-computed.
2. To return: select the borrow record from the dropdown and click **Return Product**. Return Date is set automatically to today.
3. The borrow records table shows all transactions with their current status.

### Refund Processing (Sales-Linked)

1. Open **Sales History** and select a transaction.
2. Click **Process Refund**.
3. Select only from products belonging to that sale (with remaining refundable quantity).
4. Confirm reason, quantity, and condition to complete the refund.

### Data Flow (MVC)

```
User clicks a button in the View (GUI)
    → View calls a function in the Controller (business logic)
        → Controller calls a function in the Model (database query)
            → Model executes SQL on MySQL and returns the result
        → Controller passes the result back to the View
    → View updates the table or display with the new data
```

---

## Project Structure

```
comic_book_system/
│
├── main.py                   ← Entry point — run this file to start the app
├── config.py                 ← Database and app settings (edit this for new PC)
├── setup.py                  ← Optional setup helper (installs dependencies)
├── requirements.txt          ← List of Python packages needed
├── README.md                 ← This file
│
├── database/
│   ├── __init__.py
│   ├── db_connection.py      ← Connects to MySQL using settings from config.py
│   └── comic_book_system.sql ← SQL file to create the database, tables, and sample data
│
├── models/                   ← Database operations (SQL queries)
│   ├── __init__.py
│   ├── user_model.py         ← Login authentication, user CRUD
│   ├── comic_model.py        ← Comic inventory queries
│   ├── sale_model.py         ← Sales and sale items queries
│   └── borrow_model.py       ← Borrow and return record queries
│
├── controllers/              ← Business logic (connects views to models)
│   ├── __init__.py
│   ├── login_ctrl.py         ← Validates login credentials
│   ├── dashboard_ctrl.py     ← Gathers data for dashboard cards and charts
│   ├── comics_ctrl.py        ← Handles add/edit/delete/search for comics
│   ├── pos_ctrl.py           ← Handles cart operations and completing sales
│   ├── borrow_ctrl.py        ← Handles borrow and return operations
│   ├── sales_history_ctrl.py ← Retrieves and filters sales history
│   ├── reports_ctrl.py       ← Generates report data and summaries
│   └── users_ctrl.py         ← Handles add/edit/delete for user accounts
│
├── views/                    ← GUI screens (built with PyQt6)
│   ├── __init__.py
│   ├── login_view.py         ← Login screen with username and password fields
│   ├── main_window.py        ← Main window with sidebar navigation
│   ├── dashboard_view.py     ← Dashboard with summary cards and charts
│   ├── comics_view.py        ← Comics inventory table with CRUD dialogs
│   ├── pos_view.py           ← Point of Sale interface with cart and receipt
│   ├── borrow_view.py        ← Borrow / Return form and records table
│   ├── sales_history_view.py ← Sales history table with date filtering
│   ├── reports_view.py       ← Reports page with charts (Admin only)
│   └── users_view.py         ← User management table (Admin only)
│
└── resources/
    └── fonts/                ← Bundled Inter font (Regular, Medium, SemiBold, Bold)
```

### What each folder does

| Folder         | Purpose                                                                                                                                  |
| -------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| `database/`    | Contains the MySQL connection code and the `.sql` file used to create the database.                                                      |
| `models/`      | Contains Python functions that run SQL queries (SELECT, INSERT, UPDATE, DELETE). Each file handles one table or group of related tables. |
| `controllers/` | Contains the business logic. Controllers receive requests from the views, call the appropriate model functions, and return results.      |
| `views/`       | Contains the GUI code. Each file builds one screen using PyQt6 widgets and stylesheets.                                                  |
| `resources/`   | Contains static files like fonts. The Inter font is loaded automatically on startup.                                                     |

---

## Prerequisites

Before running the system, make sure these are installed on your computer:

| Software                  | Purpose                            | Download Link                                             |
| ------------------------- | ---------------------------------- | --------------------------------------------------------- |
| **Python 3.10 or higher** | Runs the application               | [python.org/downloads](https://www.python.org/downloads/) |
| **XAMPP**                 | Provides the MySQL database server | [apachefriends.org](https://www.apachefriends.org/)       |

> **Note:** `pip` (the Python package manager) comes pre-installed with Python.

---

## Step-by-Step Installation Guide

Follow these steps to set up and run the system on a new PC or laptop.

### Step 1: Install Python

1. Download Python from [python.org/downloads](https://www.python.org/downloads/).
2. Run the installer.
3. **Important:** Check the box that says **"Add Python to PATH"** before clicking Install.
4. Verify the installation by opening a terminal (Command Prompt or PowerShell) and typing:
   ```
   python --version
   ```
   You should see something like `Python 3.12.x` or higher.

### Step 2: Install XAMPP

1. Download XAMPP from [apachefriends.org](https://www.apachefriends.org/).
2. Install it with the default settings.
3. Open the **XAMPP Control Panel**.
4. Click **Start** next to **MySQL** (you do NOT need to start Apache unless you want phpMyAdmin).

### Step 3: Copy the project folder

Copy the entire `comic_book_system` folder to the new computer (via USB, cloud drive, etc.).

### Step 4: Install Python dependencies

Open a terminal, navigate to the project folder, and run:

```bash
cd comic_book_system
pip install -r requirements.txt
```

This installs the three required packages:

- `PyQt6` — the GUI framework
- `PyQt6-Charts` — for dashboard and report charts
- `mysql-connector-python` — for connecting to MySQL

### Step 5: Import the database using phpMyAdmin

1. Make sure **MySQL is running** in XAMPP.
2. Click **Start** next to **Apache** in the XAMPP Control Panel (needed for phpMyAdmin).
3. Open your browser and go to: [http://localhost/phpmyadmin](http://localhost/phpmyadmin)
4. Click the **Import** tab at the top.
5. Click **Choose File** and select: `database/comic_book_system.sql`
6. Scroll down and click **Go**.
7. The database `comic_book_db` will be created with all tables and sample data.

> **Alternative:** You can skip this step entirely. The app will **automatically create the database** on first run if it doesn't exist.

### Step 6: Configure the database connection (if needed)

Open `config.py` and verify the settings match your MySQL setup:

```python
DB_HOST     = "localhost"
DB_USER     = "root"
DB_PASSWORD = ""              # Default XAMPP password is empty
DB_NAME     = "comic_book_db"
DB_PORT     = 3306
```

If your XAMPP MySQL uses a different password or port, update the values here. For most setups, the defaults work as-is.

### Step 7: Run the application

```bash
python main.py
```

The login screen will appear. Use one of the default accounts below to log in.

---

## Configuration (config.py)

`config.py` is the **only file you need to edit** when moving the system to another computer. It contains:

```python
# ── MySQL Database Settings ─────────────────────────────────
DB_HOST     = "localhost"       # MySQL server address
DB_USER     = "root"            # MySQL username
DB_PASSWORD = ""                # MySQL password (empty for default XAMPP)
DB_NAME     = "comic_book_db"   # Name of the database
DB_PORT     = 3306              # MySQL port number

# ── Application Settings ────────────────────────────────────
APP_TITLE           = "Comic Book Management System"
CURRENCY_SYMBOL     = "₱"       # Philippine Peso symbol
LOW_STOCK_THRESHOLD = 5         # Comics with stock below this are flagged
```

---

## Default Login Accounts

| Username | Password   | Role  | Access Level                                                          |
| -------- | ---------- | ----- | --------------------------------------------------------------------- |
| `admin`  | `admin123` | Admin | Full access (all modules including Reports and User Management)       |
| `staff`  | `staff123` | Staff | Limited access (Dashboard, Comics, POS, Borrow/Return, Sales History) |

---

## User Roles and Permissions

| Feature             | Admin | Staff |
| ------------------- | :---: | :---: |
| Dashboard           |  Yes  |  Yes  |
| Comics Inventory    |  Yes  |  Yes  |
| Point of Sale (POS) |  Yes  |  Yes  |
| Borrow / Return     |  Yes  |  Yes  |
| Sales History       |  Yes  |  Yes  |
| Reports             |  Yes  |  No   |
| User Management     |  Yes  |  No   |

---

## Philippine Localization

All dates, times, and currency values in the system follow Philippine conventions:

| Item     | Format          | Example    |
| -------- | --------------- | ---------- |
| Currency | Philippine Peso | ₱150.00    |
| Date     | DD/MM/YYYY      | 08/03/2026 |
| Time     | 12-hour clock   | 02:30 PM   |

---

## Database Tables

The system uses 5 database tables:

| Table            | Description                                                     |
| ---------------- | --------------------------------------------------------------- |
| `users`          | Stores user accounts (username, password, full name, role)      |
| `comics`         | Stores comic book inventory (title, author, price, stock, etc.) |
| `sales`          | Stores sale transaction headers (date, total, user who sold)    |
| `sale_items`     | Stores individual items within each sale (comic, qty, price)    |
| `borrow_records` | Stores borrow/return records (borrower, dates, status)          |

### Table Relationships

- Each **sale** can have multiple **sale_items** (one-to-many).
- Each **sale_item** references a **comic** from the comics table.
- Each **borrow_record** references a **comic** and the **user** who processed it.
- All sales and borrow records track which **user** created them.

---

## Architecture (MVC Pattern)

The system follows the **Model-View-Controller (MVC)** pattern, which separates the code into three layers:

```
┌─────────────────────────────────────────────────────────┐
│                        User                             │
│                    (clicks, types)                       │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                   VIEW (views/)                         │
│         GUI screens built with PyQt6 widgets            │
│    Displays data in tables, cards, charts, forms        │
└────────────────────────┬────────────────────────────────┘
                         │ calls
┌────────────────────────▼────────────────────────────────┐
│               CONTROLLER (controllers/)                 │
│       Business logic and validation rules               │
│   Receives actions from views, calls model functions    │
└────────────────────────┬────────────────────────────────┘
                         │ calls
┌────────────────────────▼────────────────────────────────┐
│                  MODEL (models/)                        │
│       Python functions that execute SQL queries         │
│   Connects to MySQL, returns data as Python dicts       │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                MySQL DATABASE (XAMPP)                    │
│          comic_book_db with 5 tables                    │
└─────────────────────────────────────────────────────────┘
```

**Why MVC?**

- **Separation of concerns** — each layer has one job, making the code easier to understand and maintain.
- **Reusability** — the same model function can be called by different controllers or views.
- **Testability** — each layer can be tested independently.

---

## Troubleshooting

| Problem                                        | Solution                                                                                                |
| ---------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| `ModuleNotFoundError: No module named 'PyQt6'` | Run `pip install -r requirements.txt` to install all dependencies.                                      |
| Cannot connect to database                     | Open XAMPP and make sure **MySQL** is started. Check `config.py` for correct settings.                  |
| Login fails with correct credentials           | Make sure the database was imported correctly. Try re-importing `comic_book_system.sql` via phpMyAdmin. |
| Charts are not showing                         | Make sure `PyQt6-Charts` is installed: `pip install PyQt6-Charts`                                       |
| App freezes or won't start                     | Check that MySQL is running in XAMPP. Look at the terminal for error messages.                          |
| `Access denied for user 'root'`                | Your MySQL has a password set. Update `DB_PASSWORD` in `config.py`.                                     |
| Tables show no data                            | The database may be empty. Re-import `comic_book_system.sql` to load sample data.                       |

---

## Technologies Used

| Technology             | Version | Purpose                          |
| ---------------------- | ------- | -------------------------------- |
| Python                 | 3.10+   | Programming language             |
| PyQt6                  | 6.5+    | GUI framework (windows, widgets) |
| PyQt6-Charts           | 6.5+    | Charts and graphs                |
| mysql-connector-python | 8.0+    | MySQL database connector         |
| MySQL (via XAMPP)      | 8.0+    | Relational database              |
| Inter Font             | 4.1     | Application typography           |
