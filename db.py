import psycopg2
import os
from datetime import datetime

# データベースに接続
def get_db_connection():
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    # テーブルが存在しない場合のみ作成する
    c.execute('''CREATE TABLE IF NOT EXISTS purchases (
                     id SERIAL PRIMARY KEY,
                     user_id TEXT,
                     item TEXT,
                     price INTEGER,
                     date DATE
                 )''')
    conn.commit()
    c.close()
    conn.close()

def add_purchase(user_id, item, price):
    conn = get_db_connection()
    c = conn.cursor()
    # プレースホルダーが ? から %s に変わります
    c.execute("INSERT INTO purchases (user_id, item, price, date) VALUES (%s, %s, %s, %s)",
              (user_id, item, price, datetime.now().date()))
    conn.commit()
    c.close()
    conn.close()

def get_monthly_total(user_id, year_month=None):
    conn = get_db_connection()
    c = conn.cursor()
    if year_month is None:
        target_month = datetime.now().strftime('%Y-%m')
    else:
        target_month = year_month

    # TO_CHAR関数で年月をテキストに変換して比較
    c.execute("""
        SELECT SUM(price) FROM purchases
        WHERE user_id=%s AND TO_CHAR(date, 'YYYY-MM')=%s
    """, (user_id, target_month))

    total = c.fetchone()[0]
    c.close()
    conn.close()
    return total or 0

def delete_purchase(user_id, item):
    conn = get_db_connection()
    c = conn.cursor()
    target_month = datetime.now().strftime('%Y-%m')

    # 削除対象を特定するため、最新の1件を削除するように変更（推奨）
    c.execute("""
        DELETE FROM purchases
        WHERE id = (
            SELECT id FROM purchases
            WHERE user_id=%s AND item=%s AND TO_CHAR(date, 'YYYY-MM')=%s
            ORDER BY date DESC, id DESC
            LIMIT 1
        )
    """, (user_id, item, target_month))

    conn.commit()
    c.close()
    conn.close()

def get_monthly_details(user_id, year_month):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
        SELECT item, price, TO_CHAR(date, 'YYYY-MM-DD') FROM purchases
        WHERE user_id=%s AND TO_CHAR(date, 'YYYY-MM')=%s
        ORDER BY date
    """, (user_id, year_month))
    rows = c.fetchall()
    c.close()
    conn.close()
    return rows
