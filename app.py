import streamlit as st
import pandas as pd
import numpy as np

from utils import load_data, add_expense, clear_data

st.set_page_config(
    page_title="Expense Tracker",
    layout="wide"
)

st.title("💰 Personal Expense Tracker")

menu = st.sidebar.selectbox(
    "Menu",
    [
        "Add Expense",
        "View Expenses",
        "Summary"
    ]
)

# -----------------------------
# Add Expense
# -----------------------------

if menu == "Add Expense":

    st.header("Add Expense")

    date = st.date_input("Date")

    category = st.selectbox(
        "Category",
        [
            "Food",
            "Travel",
            "Shopping",
            "Bills",
            "Medical",
            "Entertainment",
            "Others"
        ]
    )

    description = st.text_input("Description")

    amount = st.number_input(
        "Amount",
        min_value=0.0,
        format="%.2f"
    )

    if st.button("Save Expense"):

        add_expense(
            str(date),
            category,
            description,
            amount
        )

        st.success("Expense Saved!")

# -----------------------------
# View Expenses
# -----------------------------

elif menu == "View Expenses":

    st.header("All Expenses")

    df = load_data()

    if   st.button("🗑️ Delete All Expenses"):
         clear_data()
         st.success("All expenses deleted successfully!")
         st.rerun()

    if len(df) == 0:
        st.info("No expenses found.")
    else:
        st.dataframe(df, use_container_width=True)
        st.write(f"Total Records : {len(df)}")

# -----------------------------
# Summary
# -----------------------------

elif menu == "Summary":

    st.header("Expense Summary")

    df = load_data()

    if len(df) == 0:
        st.warning("No Data Found")

    else:

        df["Amount"] = df["Amount"].astype(float)

        total = np.sum(df["Amount"])

        average = np.mean(df["Amount"])

        maximum = np.max(df["Amount"])

        minimum = np.min(df["Amount"])

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("Total", f"₹{total:.2f}")
        c2.metric("Average", f"₹{average:.2f}")
        c3.metric("Maximum", f"₹{maximum:.2f}")
        c4.metric("Minimum", f"₹{minimum:.2f}")

        st.subheader("Category Wise")

        cat = df.groupby("Category")["Amount"].sum()

        st.bar_chart(cat)

        st.subheader("Monthly Expenses")

        df["Date"] = pd.to_datetime(df["Date"])

        monthly = df.groupby(
            df["Date"].dt.to_period("M")
        )["Amount"].sum()

        monthly.index = monthly.index.astype(str)

        st.line_chart(monthly)