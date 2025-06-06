import sqlite3

db = sqlite3.connect("UserData.db", check_same_thread=False)
c = db.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    id integer PRIMARY KEY AUTOINCREMENT,
    date text,
    amount real,
    account_id integer,
    category_id integer,
    currency text,
    payment_method text
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS accounts (
    id integer PRIMARY KEY AUTOINCREMENT,
    name text,
    type text,
    currency text,
    balance real
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS categories (
    id integer PRIMARY KEY AUTOINCREMENT,
    name text,
    type text
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS budgets (
    id integer PRIMARY KEY AUTOINCREMENT,
    categories_id integer,
    period_type text,
    amount real,
    start_date text,
    end_date text
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS currency (
    id integer PRIMARY KEY AUTOINCREMENT,
    date text,
    name text,
    usd_kzt integer,
    usd_rub integer,
    rub_kzt integer
)""")

c.execute("""
CREATE TABLE IF NOT EXISTS deposits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    target_amount REAL,
    monthly_payment REAL,
    interest_rate REAL,
    start_date TEXT,
    capitalization INTEGER, -- 1 = да, 0 = нет
    calculated_months INTEGER,
    final_amount REAL
)
""")

c.execute("DELETE FROM transactions WHERE id > 20")

db.commit()

db.close()