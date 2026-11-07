CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    opening_balance REAL NOT NULL DEFAULT 0,
    open_date TEXT NOT NULL,
    rate REAL NOT NULL DEFAULT 0,
    basis TEXT NOT NULL DEFAULT 'act365',
    auto_interest INTEGER NOT NULL DEFAULT 1,
    note TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    date TEXT NOT NULL,
    kind TEXT NOT NULL,
    amount REAL NOT NULL,
    note TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    kind TEXT NOT NULL,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    amount REAL NOT NULL,
    start_month TEXT NOT NULL,
    end_month TEXT,
    recurring INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_tx_account ON transactions(account_id, date);
