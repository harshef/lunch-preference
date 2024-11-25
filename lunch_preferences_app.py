import streamlit as st
import sqlite3
from datetime import date

# Initialize SQLite database
conn = sqlite3.connect("lunch_preferences.db")
cursor = conn.cursor()

# Create table for storing preferences
cursor.execute("""
CREATE TABLE IF NOT EXISTS preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_name TEXT NOT NULL,
    preference TEXT NOT NULL,
    date DATE NOT NULL
)
""")
conn.commit()

# Initialize session state for password and HR view refresh
if "hr_password" not in st.session_state:
    st.session_state.hr_password = "abhishek"

if "delete_clicked" not in st.session_state:
    st.session_state.delete_clicked = False

# App title
st.title("Lunch Preference Manager")

# Current date
current_date = date.today()

# Tabs for Employee and HR views
tab1, tab2 = st.tabs(["Employee View", "HR View"])

# Employee View
with tab1:
    st.header("Mark Your Lunch Preference")
    employee_name = st.text_input("Enter your name:")
    preference = st.radio("Do you want lunch today?", ["Yes", "No"])

    if st.button("Submit Preference"):
        if employee_name.strip() == "":
            st.error("Name cannot be empty!")
        else:
            # Check if the employee already submitted for today
            cursor.execute("""
            SELECT id FROM preferences WHERE employee_name = ? AND date = ?
            """, (employee_name, current_date))
            result = cursor.fetchone()

            if result:
                # Update preference
                cursor.execute("""
                UPDATE preferences SET preference = ? WHERE id = ?
                """, (preference, result[0]))
                conn.commit()
                st.success("Your preference has been updated!")
            else:
                # Insert new preference
                cursor.execute("""
                INSERT INTO preferences (employee_name, preference, date)
                VALUES (?, ?, ?)
                """, (employee_name, preference, current_date))
                conn.commit()
                st.success("Your preference has been recorded!")

# HR View
with tab2:
    st.header("HR View (Restricted Access)")
    password = st.text_input("Enter HR password:", type="password")

    if password == st.session_state.hr_password:
        st.success("Access granted!")

        # Fetch preferences for today
        if not st.session_state.delete_clicked:
            cursor.execute("""
            SELECT employee_name, preference FROM preferences WHERE date = ?
            """, (current_date,))
            data = cursor.fetchall()
        else:
            data = []  # Clear data after deletion

        # Display preferences table
        st.subheader("Today's Lunch Preferences")
        if data:
            st.table(data)

            # Count total "Yes" and "No" responses
            cursor.execute("""
            SELECT preference, COUNT(*) FROM preferences WHERE date = ? GROUP BY preference
            """, (current_date,))
            counts = cursor.fetchall()
            total_yes = sum(count for pref, count in counts if pref == "Yes")
            total_no = sum(count for pref, count in counts if pref == "No")

            # Display totals
            st.markdown(f"**Total Yes: {total_yes}**")
            st.markdown(f"**Total No: {total_no}**")
        else:
            st.info("No preferences have been recorded for today.")

        # Add button to delete data
        if st.button("Delete Today's Preferences"):
            cursor.execute("DELETE FROM preferences WHERE date = ?", (current_date,))
            conn.commit()
            st.session_state.delete_clicked = True
            st.warning("All preferences for today have been deleted.")

        # Allow HR to change the password
        st.subheader("Change Password")
        new_password = st.text_input("Enter new password:", type="password")
        confirm_password = st.text_input("Confirm new password:", type="password")

        if st.button("Update Password"):
            if new_password.strip() == "":
                st.error("Password cannot be empty!")
            elif new_password != confirm_password:
                st.error("Passwords do not match!")
            else:
                st.session_state.hr_password = new_password
                st.success("Password has been updated successfully!")
    elif password != "":
        st.error("Incorrect password!")

# Close the database connection when done
conn.close()
