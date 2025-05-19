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

# c.execute("""INSERT INTO transactions (date, amount, account_id, category_id, payment_method)
#         VALUES ("18-09-2006", 5000, 1, 1, "card")
# """)

# c.execute("DELETE FROM transactions WHERE amount > 500")

# c.execute("ALTER TABLE transactions ADD category TEXT")

c.execute("INSERT INTO categories (name) VALUES('Прочее')")

db.commit()

db.close()