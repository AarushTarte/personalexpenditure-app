import pandas as pd
import os

FILE = "expenses.csv"

COLUMNS = ["Date", "Category", "Description", "Amount"]


def load_data():
    # Create file if it doesn't exist
    if not os.path.exists(FILE):
        df = pd.DataFrame(columns=COLUMNS)
        df.to_csv(FILE, index=False)
        return df

    # Check if file is empty
    if os.path.getsize(FILE) == 0:
        df = pd.DataFrame(columns=COLUMNS)
        df.to_csv(FILE, index=False)
        return df

    try:
        return pd.read_csv(FILE)
    except pd.errors.EmptyDataError:
        df = pd.DataFrame(columns=COLUMNS)
        df.to_csv(FILE, index=False)
        return df


def save_data(df):
    df.to_csv(FILE, index=False)


def add_expense(date, category, description, amount):
    df = load_data()

    new_row = pd.DataFrame({
        "Date":[date],
        "Category":[category],
        "Description":[description],
        "Amount":[amount]
    })

    df = pd.concat([df, new_row], ignore_index=True)

    save_data(df)
