import sqlite3, json
from datetime import datetime

def init_db():
    conn = sqlite3.connect("line_balancing.db", check_same_thread=False)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS simulations(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT, target_rate REAL, actual_rate REAL,
        cycle_time REAL, stations INTEGER, efficiency REAL,
        allocation TEXT)
    """)
    conn.commit()
    return conn, c

def save_run(c, conn, target, actual, cycle, stations, eff, df):
    c.execute("""
    INSERT INTO simulations(timestamp,target_rate,actual_rate,
    cycle_time,stations,efficiency,allocation)
    VALUES(?,?,?,?,?,?,?)
    """, (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        target, actual, cycle, stations, eff,
        json.dumps(df.to_dict())
    ))
    conn.commit()

def load_runs(c):
    c.execute("SELECT id,timestamp FROM simulations ORDER BY id DESC")
    return c.fetchall()

def load_run_by_id(c, i):
    c.execute("SELECT * FROM simulations WHERE id=?", (i,))
    return c.fetchone()
