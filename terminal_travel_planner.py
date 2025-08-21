import sqlite3
import pandas as pd
import datetime
import os

# ====================================================
# PIPELINE LAYER 1: DATA HANDLER (DB for trips, users)
# ====================================================
class DataHandler:
    def __init__(self, db_name="travel_planner.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        # Trips table
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS trips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            destination TEXT,
            mode TEXT,
            cost INTEGER,
            date TEXT,
            category TEXT
        )""")
        # Users table
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT,
            security_answer TEXT
        )""")
        self.conn.commit()

    def add_trip(self, username, destination, mode, cost, date, category):
        query = """INSERT INTO trips (username, destination, mode, cost, date, category) 
                   VALUES (?, ?, ?, ?, ?, ?)"""
        self.conn.execute(query, (username, destination, mode, cost, date, category))
        self.conn.commit()

    def get_trips(self, username):
        return pd.read_sql(f"SELECT * FROM trips WHERE username='{username}'", self.conn)

    def get_user(self, username, password):
        query = "SELECT * FROM users WHERE username=? AND password=?"
        return self.conn.execute(query, (username, password)).fetchone()

    def register_user(self, username, password, security_answer):
        self.conn.execute("INSERT OR IGNORE INTO users VALUES (?, ?, ?)",
                          (username, password, security_answer))
        self.conn.commit()

    def reset_password(self, username, answer):
        query = "SELECT password FROM users WHERE username=? AND security_answer=?"
        result = self.conn.execute(query, (username, answer)).fetchone()
        return result[0] if result else None

# ====================================================
# PIPELINE LAYER 2: RECOMMENDER & BUDGET PLANNER
# ====================================================
class TravelRecommender:
    def recommend(self, budget):
        destinations = [
            ("Ooty", "Bus", 1500, "Cool Weather, Hills"),
            ("Pondicherry", "Bus", 1200, "Beach"),
            ("Munnar", "Bus", 1700, "Nature & Tea Estates"),
            ("Chennai", "Train", 300, "Hot & Busy City"),
            ("Goa", "Flight", 4800, "Beaches & Nightlife"),
        ]
        return [d for d in destinations if d[2] <= budget]

# ====================================================
# PIPELINE LAYER 3: LOGIC LAYER (Planner Features)
# ====================================================
class TravelPlanner:
    def __init__(self, username):
        self.username = username
        self.db = DataHandler()
        self.recommender = TravelRecommender()

    # ✅ Updated book_trip with cost per day & total budget
    def book_trip(self, destination, mode, cost_per_day, days, date, category, total_budget):
        # Calculate total trip cost
        trip_cost = cost_per_day * days

        if trip_cost > total_budget:
            return (f"❌ Trip cost (₹{trip_cost}) exceeds your total budget (₹{total_budget}). Booking Denied.")

        # Add trip to DB
        self.db.add_trip(self.username, destination, mode, trip_cost, date, category)

        # Calculate updated total spent
        trips = self.db.get_trips(self.username)
        total_spent = trips["cost"].sum()
        remaining_budget = total_budget - total_spent

        return (f"✅ Trip booked: {destination} for {days} days via {mode} (₹{trip_cost})\n"
                f"💰 Total spent so far: ₹{total_spent}\n"
                f"💵 Remaining budget: ₹{remaining_budget}")

    def recommend_destinations(self, budget):
        options = self.recommender.recommend(budget)
        if not options:
            return "No destinations found in this budget."
        result = "🎯 Recommended for You:\n"
        for i, (dest, mode, cost, desc) in enumerate(options, 1):
            result += f"{i}. {dest} - ₹{cost} ({desc})\n"
        return result

    def budget_planner(self, budget):
        return self.recommend_destinations(budget)

    def export_itinerary(self, filename="my_trips.txt"):
        trips = self.db.get_trips(self.username)
        if trips.empty:
            return "No trips to export."
        trips.to_csv(filename, index=False, sep="\t")
        return f"✅ Trips exported to {filename}"

    def trip_statistics(self):
        trips = self.db.get_trips(self.username)
        if trips.empty:
            return "No trips yet."
        total_trips = len(trips)
        total_cost = trips["cost"].sum()
        most_visited = trips["destination"].mode()[0]
        return (f"📊 Travel Stats:\n- Trips Planned: {total_trips}\n"
                f"- Total Spent: ₹{total_cost}\n- Most Visited: {most_visited}")

    def view_calendar(self):
        trips = self.db.get_trips(self.username)
        if trips.empty:
            return "No upcoming trips."
        trips_sorted = trips.sort_values(by="date")
        result = "🗓 Upcoming Trips:\n"
        for _, row in trips_sorted.iterrows():
            result += f"- {row['date']}: {row['destination']} via {row['mode']} (₹{row['cost']})\n"
        return result

# ====================================================
# PIPELINE LAYER 4: UI (Terminal Interaction)
# ====================================================
def main():
    db = DataHandler()
    print("🌍 Welcome to Terminal Travel Planner 🌍")
    while True:
        print("\n1. Login\n2. Register\n3. Forgot Password\n4. Exit")
        choice = input("Enter choice: ")

        if choice == "1":
            username = input("Username: ")
            password = input("Password: ")
            user = db.get_user(username, password)
            if not user:
                print("❌ Invalid credentials")
                continue
            planner = TravelPlanner(username)
            while True:
                print("\n🌐 Travel Menu")
                print("1. Book Trip")
                print("2. Recommend Destinations")
                print("3. Budget Planner")
                print("4. Export Itinerary")
                print("5. View Trip Stats")
                print("6. Calendar View")
                print("7. Logout")
                sub = input("Enter choice: ")

                if sub == "1":
                    dest = input("Destination: ")
                    mode = input("Mode (Bus/Train/Flight): ")
                    days = int(input("Number of days: "))
                    cost_per_day = int(input("Cost per day (INR): "))
                    date = input("Start Date (YYYY-MM-DD): ")
                    category = input("Category (Business/Vacation/Family/Solo): ")
                    total_budget = int(input("Your total budget (INR): "))
                    print(planner.book_trip(dest, mode, cost_per_day, days, date, category, total_budget))
                elif sub == "2":
                    budget = int(input("Enter budget (INR): "))
                    print(planner.recommend_destinations(budget))
                elif sub == "3":
                    budget = int(input("Enter budget (INR): "))
                    print(planner.budget_planner(budget))
                elif sub == "4":
                    print(planner.export_itinerary())
                elif sub == "5":
                    print(planner.trip_statistics())
                elif sub == "6":
                    print(planner.view_calendar())
                elif sub == "7":
                    break
                else:
                    print("❌ Invalid choice")

        elif choice == "2":
            username = input("Choose username: ")
            password = input("Choose password: ")
            answer = input("Security Answer (Favourite place?): ")
            db.register_user(username, password, answer)
            print("✅ Registered successfully!")

        elif choice == "3":
            username = input("Username: ")
            answer = input("Favourite place? ")
            pwd = db.reset_password(username, answer)
            print(f"✅ Your password is: {pwd}" if pwd else "❌ Invalid answer")

        elif choice == "4":
            print("Goodbye! ✈️")
            break
        else:
            print("❌ Invalid choice")

# ====================================================
if __name__ == "__main__":
    main()
