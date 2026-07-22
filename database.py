import sqlite3

conn = sqlite3.connect(
    "users.db",
    check_same_thread=False
)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS expenses(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    date TEXT,
    category TEXT,
    description TEXT,
    amount REAL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS budgets(
    username TEXT PRIMARY KEY,
    budget REAL
)
""")

conn.commit()
import pandas as pd

def load_user_expenses(username):

    query = """
SELECT
    id AS id,
    date AS Date,
    category AS Category,
    description AS Description,
    amount AS Amount
FROM expenses
WHERE username=?
"""

    return pd.read_sql_query(
        query,
        conn,
        params=(username,)
    )
def add_user_expense(username, date, category, description, amount):

    cursor.execute(
        """
        INSERT INTO expenses
        (username, date, category, description, amount)
        VALUES (?, ?, ?, ?, ?)
        """,
        (username, str(date), category, description, amount)
    )

    conn.commit()


def delete_user_expense(expense_id, username):

    cursor.execute(
        """
        DELETE FROM expenses
        WHERE id=? AND username=?
        """,
        (expense_id, username)
    )

    conn.commit()


def clear_user_expenses(username):

    cursor.execute(
        """
        DELETE FROM expenses
        WHERE username=?
        """,
        (username,)
    )

    conn.commit()


def get_budget(username):

    cursor.execute(
        """
        SELECT budget
        FROM budgets
        WHERE username=?
        """,
        (username,)
    )

    row = cursor.fetchone()

    if row:
        return row[0]

    cursor.execute(
        """
        INSERT INTO budgets(username,budget)
        VALUES(?,?)
        """,
        (username, 50000)
    )

    conn.commit()

    return 50000


def update_budget(username, budget):

    cursor.execute(
        """
        UPDATE budgets
        SET budget=?
        WHERE username=?
        """,
        (budget,username)
    )

    conn.commit()


def update_user_expense(expense_id, username, date, category, description, amount):
    cursor.execute(
        """
        UPDATE expenses
        SET date=?,
            category=?,
            description=?,
            amount=?
        WHERE id=? AND username=?
        """,
        (str(date), category, description, amount, expense_id, username)
    )

    conn.commit()
