from abc import ABC, abstractmethod
import pandas as pd
from database import load_user_expenses


class Context(ABC):
    @abstractmethod
    def load(self, username):
        """Load expense data for the given user."""

    @abstractmethod
    def summarize(self):
        """Return a useful summary of the loaded expense data."""


class ExpenseDataFrame(Context):
    def __init__(self, username):
        self.username = username
        self.data = self.load(username)

    def load(self, username):
        loaded = load_user_expenses(username)

        if loaded is None:
            return pd.DataFrame()

        if isinstance(loaded, pd.DataFrame):
            return loaded.copy()

        if isinstance(loaded, dict):
            return pd.DataFrame.from_dict(loaded)

        try:
            return pd.DataFrame(loaded)
        except Exception:
            return pd.DataFrame()

    def summarize(self):
        if self.data.empty:
            return {
                "rows": 0,
                "columns": 0,
                "total_spent": 0.0,
                "column_names": [],
                "top_category": None,
                "category_totals": {},
            }

        numeric_columns = self.data.select_dtypes(include="number")
        total_spent = float(numeric_columns.sum().sum()) if not numeric_columns.empty else 0.0

        category_totals = {}
        if "Category" in self.data.columns and "Amount" in self.data.columns:
            category_totals = (
                self.data.groupby("Category")["Amount"]
                .sum()
                .sort_values(ascending=False)
                .to_dict()
            )

        top_category = None
        if category_totals:
            top_category = max(category_totals.items(), key=lambda item: item[1])[0]

        return {
            "rows": int(len(self.data)),
            "columns": int(len(self.data.columns)),
            "total_spent": round(total_spent, 2),
            "column_names": list(self.data.columns),
            "top_category": top_category,
            "category_totals": category_totals,
        }


def get_user_data(username):
    expense_df = ExpenseDataFrame(username)
    return expense_df.data
def create_summary(df):
    if df.empty:
        return "The user has no expenses."

    summary = f"""
Total Spending: ₹{df['Amount'].sum():,.2f}

Transactions: {len(df)}

Average Expense: ₹{df['Amount'].mean():,.2f}

Highest Expense: ₹{df['Amount'].max():,.2f}

Top Category:
{df.groupby('Category')['Amount'].sum().idxmax()}
"""

    return summary
from openai import OpenAI
import streamlit as st

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
def ask_ai(question, summary):
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful personal finance assistant. "
                    "Answer only using the user's financial data. "
                    "If the answer isn't supported by the data, say so."
                ),
            },
            {
                "role": "user",
                "content": f"""
Financial Summary:

{summary}

Question:
{question}
""",
            },
        ],
        temperature=0.3,
    )

    return response.choices[0].message.content
def prepare_context(username):
    df = load_user_expenses(username)

    if df.empty:
        return "The user has no recorded expenses."

    total = df["Amount"].sum()
    avg = df["Amount"].mean()
    highest = df["Amount"].max()

    category_summary = (
        df.groupby("Category")["Amount"]
        .sum()
        .sort_values(ascending=False)
    )

    recent = df.sort_values("Date", ascending=False).head(20)

    context = f"""
Financial Summary

Total Spending: ₹{total:,.2f}
Transactions: {len(df)}
Average Expense: ₹{avg:,.2f}
Highest Expense: ₹{highest:,.2f}

Category Totals
"""

    for cat, amount in category_summary.items():
        context += f"\n- {cat}: ₹{amount:,.2f}"

    context += "\n\nRecent Transactions\n"

    for _, row in recent.iterrows():
        context += (
            f"{row['Date']} | "
            f"{row['Category']} | "
            f"{row['Description']} | "
            f"₹{row['Amount']}\n"
        )

    return context
def ask_ai(question, context):
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        temperature=0.2,
        messages=[
            {
                "role": "system",
                "content": """
You are an expert AI Financial Assistant.

Rules:
- Answer only using the supplied financial data.
- Do not invent expenses.
- If data is missing, say so.
- Give practical saving advice.
- Keep answers concise.
"""
            },
            {
                "role": "user",
                "content": f"""
User Financial Data

{context}

Question

{question}
"""
            }
        ]
    )

    return response.choices[0].message.content