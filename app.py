import streamlit as st
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import json

st.set_page_config(page_title="Expense Tracker (Priyadharshini)", layout="centered")
st.title("Expense Tracker (Priyadharshini)")
st.write("Track and record your daily expenses using this form.")

# Google Sheets Setup
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]

# Use Streamlit secrets instead of local JSON
creds_dict = json.loads(st.secrets["GCP_SERVICE_ACCOUNT"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
sheet = client.open("ExpenseTracker").sheet1

# Expense Form 
with st.form("expense_form", clear_on_submit=True):
    expense_name = st.text_input("Expense Title / Name")
    amount = st.number_input("Amount (₹)", min_value=0.0, format="%.2f", value=None)
    category = st.selectbox("Category",
        ["Select Category", "Food", "Travel", "Bills", "Shopping", "Groceries", "Health", "Entertainment", "Other"])
    date = st.date_input("Date of Expense", datetime.today())
    payment_method = st.selectbox("Payment Method",
        ["Select Method", "Cash", "UPI", "Credit Card", "Debit Card", "Net Banking"])
    shop_name = st.text_input("Shop / Merchant Name")
    location = st.text_input("Location")
    notes = st.text_area("Description / Notes (optional)")

    submit = st.form_submit_button("Save Expense")

if submit:
    if expense_name and amount > 0 and category != "Select Category" and payment_method != "Select Method":
        sheet.append_row([
            expense_name, amount, category, str(date),
            payment_method, shop_name, location, notes
        ])
        st.success("Expense saved successfully to Google Sheets.")
    else:
        st.error("Please fill all required fields properly.")

# Fetch Data and Display Totals 
data = sheet.get_all_records()

if data:
    df = pd.DataFrame(data)
    df.columns = df.columns.str.strip()
    df.columns = df.columns.str.title()
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")

    total_spent = df["Amount"].sum()
    category_totals = df.groupby("Category")["Amount"].sum().reset_index()

    st.subheader("Total Spending Summary")
    st.write(f"Total Amount Spent: ₹ {total_spent:.2f}")

    st.subheader("Category-wise Spending Summary")
    st.dataframe(category_totals)

else:
    st.info("No expenses recorded yet. Add your first entry above.")
