import os
import pandas as pd

FILE = "expenses.csv"

COLUMNS = [
    "Date",
    "Category",
    "Description",
    "Amount"
]


def load_data():

    if not os.path.exists(FILE):
        df = pd.DataFrame(columns=COLUMNS)
        df.to_csv(FILE, index=False)

    try:
        return pd.read_csv(FILE)

    except:
        df = pd.DataFrame(columns=COLUMNS)
        df.to_csv(FILE, index=False)
        return df


def save_data(df):
    df.to_csv(FILE, index=False)


def add_expense(date, category, description, amount):

    df = load_data()

    new = pd.DataFrame({

        "Date": [date],
        "Category": [category],
        "Description": [description],
        "Amount": [amount]

    })

    df = pd.concat([df, new], ignore_index=True)

    save_data(df)


def delete_expense(index):

    df = load_data()

    df = df.drop(index)

    df.reset_index(drop=True, inplace=True)

    save_data(df)


def update_expense(index, date, category, description, amount):

    df = load_data()

    df.loc[index] = [

        date,
        category,
        description,
        amount

    ]

    save_data(df)


def clear_data():
    df = pd.DataFrame(columns=COLUMNS)
    save_data(df)

from utils import *

print(load_data())
