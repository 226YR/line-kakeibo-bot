import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect('kakeibo.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS purchases (
                    id INTEGER PRIMARY KEY,
                    user_id TEXT,
                    item TEXT,
                    price INTEGER,
                    date TEXT
                )''')
    conn.commit()
    conn.close()

def add_purchase(user_id, item, price):
    conn = sqlite3.connect('kakeibo.db')
    c = conn.cursor()
    c.execute("INSERT INTO purchases (user_id, item, price, date) VALUES (?, ?, ?, ?)",
              (user_id, item, price, datetime.now().strftime('%Y-%m-%d')))
    conn.commit()
    conn.close()

def get_monthly_total(user_id, year_month=None):
    conn = sqlite3.connect('kakeibo.db')
    c = conn.cursor()
    if year_month is None:
        c.execute("""
            SELECT SUM(price) FROM purchases
            WHERE user_id=? AND strftime('%Y-%m', date)=strftime('%Y-%m', 'now')
        """, (user_id,))
    else:
        c.execute("""
            SELECT SUM(price) FROM purchases
            WHERE user_id=? AND strftime('%Y-%m', date)=?
        """, (user_id, year_month))
    total = c.fetchone()[0]
    conn.close()
    return total or 0

def delete_purchase(user_id, item):
    conn = sqlite3.connect('kakeibo.db')
    c = conn.cursor()
    c.execute("""
        DELETE FROM purchases
        WHERE user_id=? AND item=? AND strftime('%Y-%m', date)=strftime('%Y-%m', 'now')
    """, (user_id, item))
    conn.commit()
    conn.close()

def get_monthly_details(user_id, year_month):
    conn = sqlite3.connect('kakeibo.db')
    c = conn.cursor()
    c.execute("""
        SELECT item, price, date FROM purchases
        WHERE user_id=? AND strftime('%Y-%m', date)=?
        ORDER BY date
    """, (user_id, year_month))
    rows = c.fetchall()
    conn.close()
    return rows
