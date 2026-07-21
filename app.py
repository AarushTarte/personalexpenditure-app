import streamlit as st
import pandas as pd
import numpy as np

from utils import load_data, add_expense, clear_data

st.set_page_config(
    page_title="Expense Tracker",
    layout="wide"
)
st.markdown("""
<style>

.stApp{
    background: linear-gradient(135deg,#0f172a,#1e293b,#111827);
}

h1,h2,h3,label,p{
    color:white;
}

div[data-testid="stMetric"]{
    background:#1e293b;
    padding:15px;
    border-radius:15px;
    border:1px solid #334155;
}

.stButton>button{
    background:#3b82f6;
    color:white;
    border-radius:10px;
    border:none;
    padding:10px 20px;
    font-weight:bold;
}

.stButton>button:hover{
    background:#2563eb;
}

</style>
""", unsafe_allow_html=True)

st.markdown(
"""
# 💸 Personal Expense Tracker

Manage your expenses smarter.
"""
)

menu = st.sidebar.radio(
    "📁 Navigation",
    [
        "🏠 Dashboard",
        "➕ Add Expense",
        "📋 View Expenses",
        "📊 Summary"
    ]
)
# -----------------------------
# Dashboard
# -----------------------------

if menu == "🏠 Dashboard":

    st.header("📊 Expense Dashboard")

    df = load_data()

    if len(df) == 0:
        st.warning("No expenses added yet.")

    else:

        df["Amount"] = df["Amount"].astype(float)

        total = df["Amount"].sum()
        average = df["Amount"].mean()
        highest = df["Amount"].max()
        records = len(df)

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("💰 Total Spent", f"₹{total:.2f}")
        c2.metric("📊 Average", f"₹{average:.2f}")
        c3.metric("💸 Highest Expense", f"₹{highest:.2f}")
        c4.metric("🧾 Records", records)

        st.divider()

        st.subheader("📈 Monthly Expenses")

        df["Date"] = pd.to_datetime(df["Date"])

        monthly = df.groupby(
            df["Date"].dt.to_period("M")
        )["Amount"].sum()

        monthly.index = monthly.index.astype(str)

        st.line_chart(monthly)

        st.subheader("📊 Category Wise")

        category = df.groupby("Category")["Amount"].sum()

        st.bar_chart(category)
# -----------------------------
# Add Expense
# -----------------------------

if menu == "➕ Add Expense":

    st.header("Add Expense")

    date = st.date_input("Date")

    category = st.selectbox(
        "Category",
        [
            "🍕Food",
            "🚌Travel",
            "🛍Shopping",
            "💡Bills",
            "🏥Medical",
            "🎬Entertainment",
            "📦Others"
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

elif menu == "📋 View Expenses":

    st.header("📋 All Expenses")

    df = load_data()

    if st.button("🗑️ Delete All Expenses"):
        clear_data()
        st.success("All expenses deleted successfully!")
        st.rerun()

    if len(df) == 0:
        st.info("No expenses found.")
    else:
         with st.container():

          st.dataframe(
    df,
    use_container_width=True,
    height=450,
    hide_index=True
)
        

    st.write("📌 Total Records: {len(df)}")

# -----------------------------
# Summary
# -----------------------------
elif menu == "📈 Summary":
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

        c1.metric("💰 Total Spent", f"₹{total:.2f}")
        c2.metric("📊 Average", f"₹{average:.2f}")
        c3.metric("⬆ Highest", f"₹{maximum:.2f}")
        c4.metric("⬇ Lowest", f"₹{minimum:.2f}")

        with st.container():
            st.subheader("📊 Category Wise")

        cat = df.groupby("Category")["Amount"].sum()
        st.bar_chart(cat)

        with st.container():
            st.subheader("📈 Monthly Expenses")

        df["Date"] = pd.to_datetime(df["Date"])
        monthly = df.groupby(df["Date"].dt.to_period("M"))["Amount"].sum()
        monthly.index = monthly.index.astype(str)

        st.line_chart(monthly)