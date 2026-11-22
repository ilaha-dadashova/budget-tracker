"""
database.py - everything that reads or writes the SQLite database.

The database is a single file called "budget.db" that lives in this folder.
It is created automatically the first time you run the app.
"""

import random
import sqlite3
from contextlib import contextmanager
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

DB_PATH = Path(__file__).parent / "budget.db"
DEFAULT_BUDGET = 2000.0


@contextmanager
def _db():
    """Open the database, save any changes, and always close it again."""
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


# --------------------------------------------------------------------------- #
#  Setup
# --------------------------------------------------------------------------- #
def init_db():
    """Create the tables (if needed) and add sample data on the very first run."""
    with _db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS expenses (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                date      TEXT    NOT NULL,          -- stored as YYYY-MM-DD
                name      TEXT    NOT NULL,
                category  TEXT    NOT NULL,
                amount    REAL    NOT NULL,
                is_sample INTEGER NOT NULL DEFAULT 0 -- 1 = example data
            )
            """
        )
        conn.execute(
            "CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL)"
        )

        # Only add sample data once, ever. If you delete it, it stays deleted.
        already_seeded = conn.execute(
            "SELECT 1 FROM settings WHERE key = 'seeded'"
        ).fetchone()
        if not already_seeded:
            conn.executemany(
                "INSERT INTO expenses (date, name, category, amount, is_sample) "
                "VALUES (?, ?, ?, ?, 1)",
                _sample_rows(),
            )
            conn.execute("INSERT INTO settings (key, value) VALUES ('seeded', '1')")


# --------------------------------------------------------------------------- #
#  Expenses
# --------------------------------------------------------------------------- #
def load_expenses() -> pd.DataFrame:
    """Return every expense as a table (a pandas DataFrame)."""
    with _db() as conn:
        df = pd.read_sql_query(
            "SELECT id, date, name, category, amount, is_sample "
            "FROM expenses ORDER BY date DESC, id DESC",
            conn,
        )
    df["date"] = pd.to_datetime(df["date"])
    df["amount"] = df["amount"].astype(float)
    return df


def add_expense(day: date, name: str, category: str, amount: float):
    with _db() as conn:
        conn.execute(
            "INSERT INTO expenses (date, name, category, amount) VALUES (?, ?, ?, ?)",
            (day.isoformat(), name, category, round(float(amount), 2)),
        )


def delete_expense(expense_id: int):
    with _db() as conn:
        conn.execute("DELETE FROM expenses WHERE id = ?", (int(expense_id),))


def clear_sample_data():
    with _db() as conn:
        conn.execute("DELETE FROM expenses WHERE is_sample = 1")


# --------------------------------------------------------------------------- #
#  Budget setting
# --------------------------------------------------------------------------- #
def get_budget() -> float:
    with _db() as conn:
        row = conn.execute("SELECT value FROM settings WHERE key = 'budget'").fetchone()
    return float(row[0]) if row else DEFAULT_BUDGET


def set_budget(amount: float):
    with _db() as conn:
        conn.execute(
            "INSERT INTO settings (key, value) VALUES ('budget', ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (str(float(amount)),),
        )


# --------------------------------------------------------------------------- #
#  Sample data (so the dashboard isn't empty the first time you open it)
# --------------------------------------------------------------------------- #
_MONTHLY_BILLS = [  # (day of month, name, amount)
    (1, "Rent", 900.00),
    (5, "Electricity", 84.50),
    (10, "Internet", 59.99),
    (15, "Phone plan", 45.00),
]

_EVERYDAY_ITEMS = {  # category: [(name, lowest price, highest price), ...]
    "Food": [("Coffee", 3, 7), ("Groceries", 35, 110), ("Lunch", 10, 22), ("Dinner out", 25, 65)],
    "Transport": [("Uber", 8, 28), ("Gas", 35, 60), ("Bus ticket", 2.75, 2.75)],
    "Entertainment": [("Movie tickets", 12, 30), ("Concert", 45, 90), ("Video game", 20, 60)],
    "Shopping": [("Clothes", 25, 90), ("Books", 12, 35), ("Household items", 10, 45)],
    "Other": [("Gift", 20, 60), ("Haircut", 25, 40), ("Pharmacy", 8, 30)],
}
_CATEGORY_WEIGHTS = {"Food": 55, "Transport": 20, "Entertainment": 8, "Shopping": 10, "Other": 7}


def _sample_rows():
    """Make realistic-looking expenses for last month and this month (up to today)."""
    rng = random.Random(42)  # fixed seed = same sample data every time
    today = date.today()
    first_of_last_month = (today.replace(day=1) - timedelta(days=1)).replace(day=1)

    rows = []
    day = first_of_last_month
    while day <= today:
        for bill_day, name, amount in _MONTHLY_BILLS:
            if day.day == bill_day:
                rows.append((day.isoformat(), name, "Bills", amount))

        for _ in range(rng.randint(0, 2)):
            category = rng.choices(
                list(_CATEGORY_WEIGHTS), weights=list(_CATEGORY_WEIGHTS.values())
            )[0]
            name, low, high = rng.choice(_EVERYDAY_ITEMS[category])
            rows.append((day.isoformat(), name, category, round(rng.uniform(low, high), 2)))

        day += timedelta(days=1)
    return rows
