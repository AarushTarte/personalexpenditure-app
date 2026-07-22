from auth import login, signup
import streamlit as st
import pandas as pd
import plotly.express as px

from database import (
    load_user_expenses,
    add_user_expense,
    delete_user_expense,
    clear_user_expenses,
    get_budget,
    update_budget,
    update_user_expense
)
from utils import clear_data


class Divider:
    """Reusable visual separator with an optional title."""

    def __init__(self, title=None, help_text=None):
        self.title = title
        self.help_text = help_text

    def render(self):
        st.divider()

        if self.title:
            st.subheader(self.title)

        if self.help_text:
            st.caption(self.help_text)


# ==========================================
# PAGE CONFIG
# ==========================================

st.set_page_config(
    page_title="Personal Expense Tracker",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded"
)
if "logged_in" not in st.session_state:

    st.session_state.logged_in=False

if not st.session_state.logged_in:

    st.title("🔐 Personal Expense Tracker")

    page=st.radio("",["Login","Sign Up"])

    username=st.text_input("Username")

    password=st.text_input(
        "Password",
        type="password"
    )

    if page=="Login":

        if st.button("Login"):

            if login(username,password):

                st.session_state.logged_in=True

                st.session_state.username=username

                st.rerun()

            else:

                st.error("Wrong Username or Password")

    else:

        if st.button("Create Account"):

            if signup(username,password):

                st.success("Account Created!")

            else:

                st.error("Username already exists")

    st.stop()


# ==========================================
# LOAD CSS
# ==========================================

with open("style.css") as f:
    st.markdown(
        f"<style>{f.read()}</style>",
        unsafe_allow_html=True
    )

# ==========================================
# LOAD DATA
# ==========================================

df = load_user_expenses(
    st.session_state.username
)


if not df.empty:
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

# ==========================================
# SIDEBAR
# ==========================================

st.sidebar.title("💸 Expense Tracker")

menu = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Dashboard",
        "➕ Add Expense",
        "📋 Transactions",
        "📊 Analytics"
    ]
)
if st.sidebar.button("🚪 Logout"):

    st.session_state.logged_in = False

    st.session_state.username = ""

    st.rerun()

st.sidebar.markdown("---")

st.sidebar.markdown("---")

st.sidebar.markdown("## 📌 Quick Stats")

budget = get_budget(st.session_state.username)

st.sidebar.metric(
    "💰 Total",
    f"₹{df['Amount'].sum():,.0f}" if not df.empty else "₹0"
)

st.sidebar.metric(
    "🧾 Transactions",
    len(df)
)

st.sidebar.metric(
    "📂 Categories",
    df["Category"].nunique() if not df.empty else 0
)
st.sidebar.markdown("---")

new_budget = st.sidebar.number_input(
    "💰 Monthly Budget (₹)",
    min_value=1000,
    value=int(budget),
    step=500
)

if new_budget != budget:

    update_budget(
        st.session_state.username,
        new_budget
    )

    budget = new_budget

# ==========================================
# DASHBOARD
# ==========================================

if menu == "🏠 Dashboard":

    st.markdown("""
# 💸 Personal Expense Tracker

""")

    total_spent = 0

    if not df.empty:
        total_spent = df["Amount"].sum()

    total_transactions = len(df)

    total_categories = 0

    if not df.empty:
        total_categories = df["Category"].nunique()

    remaining = max(budget - total_spent, 0)

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "💰 Total Spent",
        f"₹{total_spent:,.2f}",
        "Current Total"
    )

    c2.metric(
        "💵 Remaining",
        f"₹{remaining:,.2f}",
        "Budget Left"
    )

    c3.metric(
        "📂 Categories",
        total_categories,
        "Tracked"
    )

    c4.metric(
        "🧾 Transactions",
        total_transactions,
        "Recorded"
    )

    st.divider()

    st.subheader("Budget Usage")

    progress = 0

    if budget > 0:
        progress = min(total_spent / budget, 1.0)

    st.progress(progress)

    st.write(
        f"Budget Used: ₹{total_spent:,.2f} / ₹{budget:,.2f}"
    )

    st.subheader("🏆 Financial Health")

    health = max(0, 100 - (total_spent / budget) * 100) if budget > 0 else 100

    st.progress(health / 100)

    st.success(f"Financial Health Score: {health:.1f}/100")
    # ==========================================
    # SPENDING INSIGHT
    # ==========================================

    st.divider()

    st.subheader("💡 Spending Insight")

    if not df.empty:

        top_category = (
            df.groupby("Category")["Amount"]
            .sum()
            .idxmax()
        )

        top_amount = (
            df.groupby("Category")["Amount"]
            .sum()
            .max()
        )

        st.info(
            f"Your highest spending is on **{top_category}** "
            f"(₹{top_amount:,.2f})."
        )

    else:

        st.info("No expense data available.")

    # ==========================================
    # CHARTS
    # ==========================================

    st.divider()

    left, right = st.columns(2)

    with left:

        st.subheader("📈 Monthly Spending Trend")

        if not df.empty:

            monthly = (
                df.groupby(df["Date"].dt.to_period("M"))["Amount"]
                .sum()
                .reset_index()
            )

            monthly["Date"] = monthly["Date"].astype(str)

            fig = px.line(
                monthly,
                x="Date",
                y="Amount",
                markers=True,
                template="plotly_dark"
            )

            fig.update_layout(
                height=400,
                xaxis_title="Month",
                yaxis_title="Amount (₹)",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        else:

            st.info("No chart data available.")

    with right:

        st.subheader("🍩 Category Distribution")

        if not df.empty:

            category = (
                df.groupby("Category")["Amount"]
                .sum()
                .reset_index()
            )

            fig = px.pie(
                category,
                names="Category",
                values="Amount",
                hole=0.65,
                template="plotly_dark"
            )

            fig.update_layout(
                height=400,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        else:

            st.info("No chart data available.")

    # ==========================================
    # CATEGORY BAR CHART
    # ==========================================

    st.divider()

    st.subheader("📊 Category-wise Spending")

    if not df.empty:

        category_bar = (
            df.groupby("Category")["Amount"]
            .sum()
            .sort_values(ascending=False)
            .reset_index()
        )

        fig = px.bar(
            category_bar,
            x="Category",
            y="Amount",
            text_auto=True,
            template="plotly_dark"
        )

        fig.update_layout(
            height=450,
            xaxis_title="Category",
            yaxis_title="Amount (₹)",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:

        st.info("No chart data available.")

    # ==========================================
    # DAILY SPENDING
    # ==========================================

    st.divider()

    st.subheader("📅 Daily Spending")

    if not df.empty:

        daily = (
            df.groupby("Date")["Amount"]
            .sum()
            .reset_index()
        )

        fig = px.area(
            daily,
            x="Date",
            y="Amount",
            template="plotly_dark"
        )

        fig.update_layout(
            height=400,
            xaxis_title="Date",
            yaxis_title="Amount (₹)",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:

        st.info("No chart data available.")

    # ==========================================
    # RECENT TRANSACTIONS
    # ==========================================

    st.divider()

    st.subheader("🧾 Recent Transactions")

    if not df.empty:

        recent = (
            df.sort_values(
                "Date",
                ascending=False
            )
            .head(10)
        )

        st.dataframe(
            recent,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info("No transactions available.")
        # ==========================================
# ADD EXPENSE PAGE
# ==========================================

elif menu == "➕ Add Expense":

    st.title("➕ Add New Expense")

    st.write("Fill in the details below to add a new expense.")

    with st.form("expense_form", clear_on_submit=True):

        date = st.date_input("📅 Date")

        category = st.selectbox(
            "📂 Category",
            [
                "Food",
                "Transport",
                "Shopping",
                "Entertainment",
                "Bills",
                "Health",
                "Education",
                "Travel",
                "Other"
            ]
        )

        description = st.text_input(
            "📝 Description"
        )

        amount = st.number_input(
            "💰 Amount (₹)",
            min_value=0.0,
            format="%.2f"
        )

        submit = st.form_submit_button(
            "➕ Add Expense"
        )

    if submit:

        if description.strip() == "":

            st.error("Please enter a description.")

        elif amount <= 0:

            st.error("Amount must be greater than 0.")

        else:

            add_user_expense(
                st.session_state.username,
                date,
                category,
                description,
                amount
            )

            st.success("✅ Expense Added Successfully!")

            st.balloons()

            st.rerun()

    st.divider()

    st.subheader("Expense Categories")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.info("🍔 Food")

        st.info("🚌 Transport")

        st.info("🛍 Shopping")

    with col2:

        st.info("🎬 Entertainment")

        st.info("💡 Bills")

        st.info("🏥 Health")

    with col3:

        st.info("📚 Education")

        st.info("✈ Travel")

        st.info("📦 Other")
        # ==========================================
# TRANSACTIONS PAGE
# ==========================================

elif menu == "📋 Transactions":

    st.title("📋 Transactions")

    if df.empty:

        st.warning("No expenses found. Add some expenses first.")

    else:

        # --------------------------------------
        # SEARCH & FILTERS
        # --------------------------------------

        st.subheader("🔍 Search & Filters")

        col1, col2, col3 = st.columns(3)

        with col1:

            search = st.text_input(
                "Search Description"
            )

        with col2:

            categories = ["All"] + sorted(df["Category"].unique().tolist())

            selected_category = st.selectbox(
                "Category",
                categories
            )

        with col3:

            min_amount = float(df["Amount"].min())
            max_amount = float(df["Amount"].max())

            if min_amount == max_amount:

                st.info(f"All expenses are ₹{min_amount:.2f}")

                amount_range = (min_amount, max_amount)

            else:

                amount_range = st.slider(
                    "Amount Range (₹)",
                    min_value=min_amount,
                    max_value=max_amount,
                    value=(min_amount, max_amount),
                    step=1.0
                )

        filtered_df = df.copy()

        if search:

            filtered_df = filtered_df[
                filtered_df["Description"]
                .str.contains(search, case=False, na=False)
            ]

        if selected_category != "All":

            filtered_df = filtered_df[
                filtered_df["Category"] == selected_category
            ]

        filtered_df = filtered_df[
            (filtered_df["Amount"] >= amount_range[0]) &
            (filtered_df["Amount"] <= amount_range[1])
        ]

        # --------------------------------------
        # TABLE
        # --------------------------------------

        st.divider()

        st.subheader("🧾 All Transactions")

        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True,
            height=450
        )

        st.divider()

        st.subheader("✏️ Edit Expense")

        edit_id = st.selectbox(
            "Select Expense to Edit",
            filtered_df["id"]
        )

        expense = filtered_df[filtered_df["id"] == edit_id].iloc[0]

        new_date = st.date_input(
            "Date",
            pd.to_datetime(expense["Date"]).date()
        )

        new_category = st.selectbox(
            "Category",
            [
                "Food",
                "Transport",
                "Shopping",
                "Entertainment",
                "Bills",
                "Health",
                "Education",
                "Travel",
                "Other"
            ],
            index=[
                "Food",
                "Transport",
                "Shopping",
                "Entertainment",
                "Bills",
                "Health",
                "Education",
                "Travel",
                "Other"
            ].index(expense["Category"])
        )

        new_description = st.text_input(
            "Description",
            expense["Description"]
        )

        new_amount = st.number_input(
            "Amount",
            min_value=0.0,
            value=float(expense["Amount"])
        )

        if st.button("💾 Save Changes"):

            update_user_expense(
                edit_id,
                st.session_state.username,
                new_date,
                new_category,
                new_description,
                new_amount
            )

            st.success("Expense updated successfully!")

            st.rerun()

        # --------------------------------------
        # DELETE EXPENSE
        # --------------------------------------

        st.divider()

        st.subheader("🗑 Delete Expense")

        delete_id = st.selectbox(
            "Select Expense",
            filtered_df["id"],
            format_func=lambda x:
                f"{filtered_df.loc[filtered_df['id'] == x, 'Date'].iloc[0].date()} | "
                f"{filtered_df.loc[filtered_df['id'] == x, 'Category'].iloc[0]} | "
                f"{filtered_df.loc[filtered_df['id'] == x, 'Description'].iloc[0]} | "
                f"₹{filtered_df.loc[filtered_df['id'] == x, 'Amount'].iloc[0]:.2f}"
        )

        if st.button("Delete Selected Expense"):
            delete_user_expense(
                delete_id,
                st.session_state.username
            )

            st.success("Expense deleted successfully!")

            st.rerun()

        # --------------------------------------
        # DELETE ALL
        # --------------------------------------

        Divider("⚠ Delete All Expenses").render()

        if st.button("Delete All Expenses"):
            clear_user_expenses(
                st.session_state.username
            )

            st.success("All your expenses have been deleted.")

            st.rerun()

        # --------------------------------------
        # DOWNLOAD CSV
        # --------------------------------------

        st.divider()

        csv = filtered_df.to_csv(index=False)

        st.download_button(
            label="📥 Download Transactions CSV",
            data=csv,
            file_name="expenses.csv",
            mime="text/csv",
        )

# ==========================================
# ANALYTICS PAGE
# ==========================================

elif menu == "📊 Analytics":

    st.title("📊 Expense Analytics")

    if df.empty:

        st.warning("No expense data available for analysis.")

    else:

        # ==========================================
        # KPI CARDS
        # ==========================================

        total_spent = df["Amount"].sum()
        avg_expense = df["Amount"].mean()
        max_expense = df["Amount"].max()
        total_categories = df["Category"].nunique()

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "💰 Total Spending",
            f"₹{total_spent:,.2f}"
        )

        c2.metric(
            "📈 Average Expense",
            f"₹{avg_expense:,.2f}"
        )

        c3.metric(
            "🔥 Highest Expense",
            f"₹{max_expense:,.2f}"
        )

        c4.metric(
            "📂 Categories",
            total_categories
        )

        st.divider()

        # ==========================================
        # MONTHLY TREND
        # ==========================================

        left, right = st.columns(2)

        with left:

            st.subheader("📈 Monthly Spending")

            monthly = (
                df.groupby(df["Date"].dt.to_period("M"))["Amount"]
                .sum()
                .reset_index()
            )

            monthly["Date"] = monthly["Date"].astype(str)

            fig = px.line(
                monthly,
                x="Date",
                y="Amount",
                markers=True,
                template="plotly_dark"
            )

            fig.update_layout(
                height=400,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        # ==========================================
        # CATEGORY DONUT
        # ==========================================

        with right:

            st.subheader("🍩 Category Distribution")

            category = (
                df.groupby("Category")["Amount"]
                .sum()
                .reset_index()
            )

            fig = px.pie(
                category,
                names="Category",
                values="Amount",
                hole=0.65,
                template="plotly_dark"
            )

            fig.update_layout(
                height=400,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        st.divider()

        # ==========================================
        # CATEGORY BAR CHART
        # ==========================================

        st.subheader("📊 Category-wise Spending")

        category_bar = (
            df.groupby("Category")["Amount"]
            .sum()
            .sort_values(ascending=False)
            .reset_index()
        )

        fig = px.bar(
            category_bar,
            x="Category",
            y="Amount",
            text_auto=True,
            template="plotly_dark"
        )

        fig.update_layout(
            height=450,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.divider()

        # ==========================================
        # DAILY SPENDING
        # ==========================================

        st.subheader("📅 Daily Spending Trend")

        daily = (
            df.groupby("Date")["Amount"]
            .sum()
            .reset_index()
        )

        fig = px.area(
            daily,
            x="Date",
            y="Amount",
            template="plotly_dark"
        )

        fig.update_layout(
            height=400,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.divider()

        # ==========================================
        # TOP 5 EXPENSES
        # ==========================================

        st.subheader("🏆 Top 5 Highest Expenses")

        top_expenses = (
            df.sort_values(
                "Amount",
                ascending=False
            )
            .head(5)
        )

        st.dataframe(
            top_expenses,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        # ==========================================
        # SMART INSIGHTS
        # ==========================================

        st.subheader("🧠 Smart Spending Insights")

        highest_category = (
            df.groupby("Category")["Amount"]
            .sum()
            .idxmax()
        )

        highest_amount = (
            df.groupby("Category")["Amount"]
            .sum()
            .max()
        )

        st.info(
            f"""
### 📌 Spending Summary

• Total Spending : ₹{total_spent:,.2f}

• Highest Category : **{highest_category}**

• Amount Spent : ₹{highest_amount:,.2f}

• Average Expense : ₹{avg_expense:,.2f}

💡 Recommendation:

Try reducing spending in **{highest_category}**
by 10-15% to improve your monthly savings.
"""
        )

        st.divider()

        # ==========================================
        # PDF EXPORT
        # ==========================================

        st.subheader("📄 Export Report")

        if st.button("Generate PDF Report"):

            from fpdf import FPDF

            pdf = FPDF()

            pdf.add_page()

            pdf.set_font("Arial", "B", 18)

            pdf.cell(
                200,
                10,
                "Expense Report",
                ln=True,
                align="C"
            )

            pdf.ln(10)

            pdf.set_font("Arial", "", 12)

            pdf.cell(
                200,
                10,
                f"Total Spending : Rs. {total_spent:,.2f}",
                ln=True
            )

            pdf.cell(
                200,
                10,
                f"Average Expense : Rs.{avg_expense:,.2f}",
                ln=True
            )

            pdf.cell(
                200,
                10,
                f"Highest Category : {highest_category}",
                ln=True
            )

            pdf.output("Expense_Report.pdf")

            with open(
                "Expense_Report.pdf",
                "rb"
            ) as file:

                st.download_button(

                    "⬇ Download PDF",

                    file,

                    file_name="Expense_Report.pdf"
                )

            st.success("PDF Generated Successfully!")