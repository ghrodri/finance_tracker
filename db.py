import sqlite3
from contextlib import closing
from functools import lru_cache

from config import DB_PATH, SQL_DIR


@lru_cache(maxsize=None)
def load_sql(name):
    return (SQL_DIR / f"{name}.sql").read_text()


def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with closing(connect()) as conn:
        conn.executescript(load_sql("schema"))
        conn.commit()


def fetch(name, args=()):
    # run sql/<name>.sql and return a list of dicts
    with closing(connect()) as conn:
        return [dict(row) for row in conn.execute(load_sql(name), args).fetchall()]


def execute(name, args=()):
    # run sql/<name>.sql and return the last inserted id
    with closing(connect()) as conn:
        cur = conn.execute(load_sql(name), args)
        conn.commit()
        return cur.lastrowid
