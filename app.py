import streamlit as st
from datetime import datetime
from terminal_travel_planner import DataHandler, TravelPlanner  # Import your classes from the above code

db = DataHandler()


if 'login_status' not in st.session_state:
    st.session_state['login_status'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ""

def login_user(username, password):
    user = db.get_user(username, password)
    if user:
        st.session_state['login_status'] = True
        st.session_state['username'] = username
        st.success(f"Welcome, {username}!")
    else:
        st.error("❌ Invalid credentials")

def register_user(username, password, answer):
    db.register_user(username, password, answer)
    st.success("✅ Registered successfully!")

def reset_password(username, answer):
    pwd = db.reset_password(username, answer)
    if pwd:
        st.success(f"✅ Your password is: {pwd}")
    else:
        st.error("❌ Invalid answer")


st.title("🌍 Terminal Travel Planner - Web Edition")

if not st.session_state['login_status']:
    auth_choice = st.radio("Login / Register / Forgot Password", ["Login", "Register", "Forgot Password"])
    
    if auth_choice == "Login":
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            login_user(username, password)

    elif auth_choice == "Register":
        username = st.text_input("Choose Username")
        password = st.text_input("Choose Password", type="password")
        answer = st.text_input("Security Answer (Favourite place?)")
        if st.button("Register"):
            register_user(username, password, answer)

    elif auth_choice == "Forgot Password":
        username = st.text_input("Username")
        answer = st.text_input("Favourite place?")
        if st.button("Reset Password"):
            reset_password(username, answer)

else:
    planner = TravelPlanner(st.session_state['username'])
    menu = st.sidebar.selectbox("Menu", ["Book Trip", "Recommend Destinations", 
                                         "Budget Planner", "Export Itinerary", 
                                         "View Trip Stats", "Calendar View", "Logout"])
    
    if menu == "Book Trip":
        st.subheader("📌 Book a Trip")
        dest = st.text_input("Destination")
        mode = st.selectbox("Mode", ["Bus", "Train", "Flight"])
        days = st.number_input("Number of Days", min_value=1, step=1)
        cost_per_day = st.number_input("Cost per Day (INR)", min_value=0)
        date = st.date_input("Start Date")
        category = st.selectbox("Category", ["Business", "Vacation", "Family", "Solo"])
        total_budget = st.number_input("Your Total Budget (INR)", min_value=0)
        if st.button("Book Trip"):
            result = planner.book_trip(dest, mode, cost_per_day, days, date.strftime("%Y-%m-%d"), category, total_budget)
            st.info(result)

    elif menu == "Recommend Destinations":
        st.subheader("🎯 Destination Recommendations")
        budget = st.number_input("Enter Budget (INR)", min_value=0)
        if st.button("Show Recommendations"):
            st.text(planner.recommend_destinations(budget))

    elif menu == "Budget Planner":
        st.subheader("💰 Budget Planner")
        budget = st.number_input("Enter Budget (INR) for Planner", min_value=0)
        if st.button("Plan Budget"):
            st.text(planner.budget_planner(budget))

    elif menu == "Export Itinerary":
        st.subheader("📄 Export Itinerary")
        filename = st.text_input("Filename (e.g., my_trips.txt)", value="my_trips.txt")
        if st.button("Export"):
            result = planner.export_itinerary(filename)
            st.success(result)

    elif menu == "View Trip Stats":
        st.subheader("📊 Trip Statistics")
        st.text(planner.trip_statistics())

    elif menu == "Calendar View":
        st.subheader("🗓 Upcoming Trips")
        st.text(planner.view_calendar())

    elif menu == "Logout":
        st.session_state['login_status'] = False
        st.session_state['username'] = ""
        st.success("Logged out successfully!")
