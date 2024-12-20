import streamlit as st
from supabase import create_client
from datetime import datetime, date
import pytz

SUPABASE_URL = "https://begzsfzumhzowutdfegx.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJlZ3pzZnp1bWh6b3d1dGRmZWd4Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczMjUwODExNSwiZXhwIjoyMDQ4MDg0MTE1fQ.WrzeC7DgRdheuIWeL1E0Sng5LLEPbGpnCB5asKqfNaI"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

if "delete_clicked" not in st.session_state:
    st.session_state.delete_clicked = False

response = supabase.table("settings").select("value").eq("key", "hr_password").execute()
stored_password = response.data[0]["value"] if response.data else "abhishek"
if "hr_password" not in st.session_state:
    st.session_state.hr_password = stored_password

ist = pytz.timezone("Asia/Kolkata")
today_date = datetime.now(ist).strftime("%B %d, %Y")
st.title(f"Conversenow Lunch Preferences")
st.subheader(f"{today_date}")

tab1, tab2 = st.tabs(["Employee View", "HR View"])

with tab1:
    st.header("Employee View")
    employee_name = st.text_input("Enter your name:")
    preference = st.radio("Do you want lunch today?", ("Yes", "No"))

    if st.button("Submit"):
        if employee_name.strip() == "":
            st.error("Name cannot be empty!")
        else:
            current_time = datetime.now(ist).isoformat()
            supabase.table("preferences").insert({
                "employee_name": employee_name,
                "preference": preference,
                "created_at": current_time
            }).execute()
            st.success("Your preference has been recorded!")

with tab2:
    st.header("HR View")

    hr_username = st.text_input("Enter HR username:")
    hr_password = st.text_input("Enter HR password:", type="password")

    if hr_username and hr_password:
        response = supabase.table("hr_users").select("*").eq("username", hr_username).execute()
        hr_user = response.data[0] if response.data else None
        
        if hr_user and hr_user["password"] == hr_password:
            st.success("Access granted!")
            selected_date = st.date_input("Select a date to view preferences", value=date.today())

            response = supabase.table("preferences").select("*").execute()
            preferences = response.data if response.data else []
            filtered_preferences = [
                {
                    "Name": pref["employee_name"],
                    "Preference": pref["preference"],
                    "Time": datetime.fromisoformat(pref["created_at"]).strftime("%H:%M %p"),
                }
                for pref in preferences
                if pref["created_at"][:10] == selected_date.isoformat()
            ]
            
            st.subheader(f"Preferences for {selected_date}")
            if filtered_preferences:
                st.table(filtered_preferences)
                yes_count = sum(1 for entry in filtered_preferences if entry["Preference"] == "Yes")
                no_count = sum(1 for entry in filtered_preferences if entry["Preference"] == "No")
                st.markdown(f"**Total Yes: {yes_count} | Total No: {no_count}**")
            else:
                st.info("No preferences have been recorded for this date.")
            
            if st.button(f"Delete Preferences for {selected_date}"):
                supabase.rpc("delete_todays_preferences", {"date": selected_date.isoformat()}).execute()
                st.session_state.delete_clicked = True
                st.warning(f"All preferences for {selected_date} have been deleted!")

            st.subheader("Change Password")
            new_password = st.text_input("Enter new password:", type="password")
            confirm_password = st.text_input("Confirm new password:", type="password")

            if st.button("Update Password"):
                if new_password.strip() == "":
                    st.error("Password cannot be empty!")
                elif new_password != confirm_password:
                    st.error("Passwords do not match!")
                else:
                    supabase.table("hr_users").update({"password": new_password}).eq("username", hr_username).execute()
                    st.session_state.hr_password = new_password
                    st.success("Password has been updated successfully!")
        else:
            st.error("Incorrect username or password!")

