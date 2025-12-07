#!/usr/bin/env python3
"""
Vista Verde Apartments - RMS (Main Application)
Owner: Ford Asuncion
"""
import tkinter as tk
from tkinter import ttk
import sqlite3
import os

# Import page modules
from pages.home_page import HomePage
from pages.analytics_page import AnalyticsPage
from pages.units_page import UnitsPage
from pages.tenants_page import TenantsPage
from pages.payments_page import PaymentsPage

# Import database functions
try:
    from database import create_database, insert_sample_data, DB_NAME
    HAS_DATABASE_MODULE = True
except ImportError:
    HAS_DATABASE_MODULE = False
    DB_NAME = "vista_verde.db"

def init_db():
    """Initialize database"""
    if not os.path.exists(DB_NAME):
        if HAS_DATABASE_MODULE:
            print("📦 Database not found. Creating from database.py...")
            conn, cur = create_database()
            if conn and cur:
                insert_sample_data(conn, cur)
                conn.close()
                print("✅ Database created successfully!")
        else:
            print("⚠️ Warning: database.py not found. Creating basic structure...")
            conn = sqlite3.connect(DB_NAME)
            cur = conn.cursor()
            cur.execute('''CREATE TABLE IF NOT EXISTS units (
                id INTEGER PRIMARY KEY AUTOINCREMENT, unit_number TEXT UNIQUE NOT NULL,
                unit_type TEXT, monthly_rent REAL, is_occupied INTEGER DEFAULT 0, created_at TEXT)''')
            cur.execute('''CREATE TABLE IF NOT EXISTS tenants (
                id INTEGER PRIMARY KEY AUTOINCREMENT, full_name TEXT NOT NULL, email TEXT, phone TEXT,
                unit_id INTEGER, move_in_date TEXT, monthly_rent REAL,
                FOREIGN KEY (unit_id) REFERENCES units (id) ON DELETE SET NULL)''')
            cur.execute('''CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER, amount REAL,
                payment_date TEXT, month_covered TEXT,
                FOREIGN KEY (tenant_id) REFERENCES tenants (id) ON DELETE CASCADE)''')
            cur.execute('''CREATE TABLE IF NOT EXISTS utility_bills (
                id INTEGER PRIMARY KEY AUTOINCREMENT, bill_type TEXT NOT NULL, amount REAL NOT NULL,
                billing_month TEXT NOT NULL, due_date TEXT, paid INTEGER DEFAULT 0, created_at TEXT)''')
            conn.commit()
            conn.close()
            print("✅ Basic database structure created.")

class VistaVerdeApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Vista Verde Apartments - RMS")
        self.geometry("1450x900")
        self.minsize(1300, 750)
        self.configure(bg="#f0f4f8")
        
        self.user_data = {
            "first_name": "Ford", "last_name": "Asuncion",
            "email": "Ford@gmail.com", "phone": "09817225237",
            "location": "Nasugbu, Batangas, Brgy 6 Phugo st."
        }
        
        init_db()
        self.check_database_status()
        self.create_sidebar()
        self.create_main_area()
        
        # Initialize pages
        self.home_page = HomePage(self.main_frame, self)
        self.analytics_page = AnalyticsPage(self.main_frame, self)
        self.units_page = UnitsPage(self.main_frame, self)
        self.tenants_page = TenantsPage(self.main_frame, self)
        self.payments_page = PaymentsPage(self.main_frame, self)
        
        # Show home by default
        self.show_home()

    def check_database_status(self):
        try:
            conn = sqlite3.connect(DB_NAME)
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM units"); unit_count = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM tenants"); tenant_count = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM payments"); payment_count = cur.fetchone()[0]
            conn.close()
            print(f"\n{'='*50}\n📊 Vista Verde Database Status\n{'='*50}")
            print(f"🏢 Units: {unit_count}\n👥 Tenants: {tenant_count}\n💰 Payments: {payment_count}\n{'='*50}\n")
            if unit_count == 0:
                print("💡 Tip: Run 'python database.py' to add sample data!")
        except sqlite3.Error as e:
            print(f"⚠️ Database check warning: {e}")

    def create_sidebar(self):
        sidebar = tk.Frame(self, bg="#2c3e50", width=270)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        
        tk.Label(sidebar, text="Vista Verde\nApartments", font=("Helvetica", 18, "bold"),
                 fg="white", bg="#2c3e50", justify="center").pack(pady=70)
        
        menu = [
            ("Home", self.show_home),
            ("Analytics", self.show_analytics),
            ("Units", self.show_units),
            ("Tenants", self.show_tenants),
            ("Payments", self.show_payments),
            ("Logout", self.destroy)
        ]
        
        for text, cmd in menu:
            btn = tk.Button(sidebar, text=text, font=("Helvetica", 13), bg="#2c3e50", fg="white",
                          bd=0, anchor="w", padx=55, pady=22, command=cmd, cursor="hand2")
            btn.pack(fill="x")
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#34495e"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#2c3e50"))

    def create_main_area(self):
        self.main_frame = tk.Frame(self, bg="#f0f4f8")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

    def clear_main(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def show_home(self):
        self.clear_main()
        self.home_page = HomePage(self.main_frame, self)
        self.home_page.show()

    def show_analytics(self):
        self.clear_main()
        self.analytics_page = AnalyticsPage(self.main_frame, self)
        self.analytics_page.show()

    def show_units(self):
        self.clear_main()
        self.units_page = UnitsPage(self.main_frame, self)
        self.units_page.show()

    def show_tenants(self):
        self.clear_main()
        self.tenants_page = TenantsPage(self.main_frame, self)
        self.tenants_page.show()

    def show_payments(self):
        self.clear_main()
        self.payments_page = PaymentsPage(self.main_frame, self)
        self.payments_page.show()

if __name__ == "__main__":
    print("\n" + "="*50)
    print("🏢 Vista Verde Apartments RMS")
    print("="*50)
    app = VistaVerdeApp()
    app.mainloop()
