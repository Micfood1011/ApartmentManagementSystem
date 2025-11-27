#!/usr/bin/env python3
"""
Vista Verde Apartments - FULL RMS (Fixed & Clean)
Owner: Ford Asuncion

This application connects to the database created by database.py
Run database.py first to set up the database!
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import sqlite3
import os

# Import database functions
try:
    from database import create_database, insert_sample_data, DB_NAME
    HAS_DATABASE_MODULE = True
except ImportError:
    HAS_DATABASE_MODULE = False
    DB_NAME = "vista_verde.db"

def init_db():
    """Initialize database - use database.py functions if available"""
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
            
            cur.execute('''
                CREATE TABLE IF NOT EXISTS units (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    unit_number TEXT UNIQUE NOT NULL,
                    unit_type TEXT,
                    monthly_rent REAL,
                    is_occupied INTEGER DEFAULT 0,
                    created_at TEXT
                )
            ''')
            
            cur.execute('''
                CREATE TABLE IF NOT EXISTS tenants (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    full_name TEXT NOT NULL,
                    email TEXT,
                    phone TEXT,
                    unit_id INTEGER,
                    move_in_date TEXT,
                    monthly_rent REAL,
                    FOREIGN KEY (unit_id) REFERENCES units (id) ON DELETE SET NULL
                )
            ''')
            
            cur.execute('''
                CREATE TABLE IF NOT EXISTS payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER,
                    amount REAL,
                    payment_date TEXT,
                    month_covered TEXT,
                    FOREIGN KEY (tenant_id) REFERENCES tenants (id) ON DELETE CASCADE
                )
            ''')
            
            conn.commit()
            conn.close()
            print("✅ Basic database structure created.")
            print("💡 Run 'python database.py' for sample data and triggers!")

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

        # Initialize database
        init_db()
        
        # Check database connection
        self.check_database_status()
        
        self.create_sidebar()
        self.create_main_area()
        self.show_home()

    def check_database_status(self):
        """Check if database has data and show status"""
        try:
            conn = sqlite3.connect(DB_NAME)
            cur = conn.cursor()
            
            cur.execute("SELECT COUNT(*) FROM units")
            unit_count = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM tenants")
            tenant_count = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM payments")
            payment_count = cur.fetchone()[0]
            
            conn.close()
            
            print(f"\n{'='*50}")
            print(f"📊 Vista Verde Database Status")
            print(f"{'='*50}")
            print(f"🏢 Units: {unit_count}")
            print(f"👥 Tenants: {tenant_count}")
            print(f"💰 Payments: {payment_count}")
            print(f"{'='*50}\n")
            
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
            ("Profile", self.show_profile),
            ("Units", self.show_units),
            ("Tenants", self.show_tenants),
            ("Payments", self.show_payments),
            ("Logout", self.destroy)
        ]

        for text, cmd in menu:
            btn = tk.Button(sidebar, text=text, font=("Helvetica", 13),
                            bg="#2c3e50", fg="white", bd=0, anchor="w",
                            padx=55, pady=22, command=cmd, cursor="hand2")
            btn.pack(fill="x")
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#34495e"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#2c3e50"))

    def create_main_area(self):
        self.main_frame = tk.Frame(self, bg="#f0f4f8")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

    def clear_main(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    # ==================== HOME ====================
    def show_home(self):
        self.clear_main()
        canvas = tk.Canvas(self.main_frame, bg="#00a8b5", highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        center = tk.Frame(canvas, bg="#00a8b5")
        center.place(relx=0.5, rely=0.5, anchor="center")

        logo = tk.Canvas(center, width=340, height=340, bg="#00a8b5", highlightthickness=0)
        logo.pack()
        logo.create_oval(40, 40, 300, 300, fill="white", outline="#00d4c0")
        logo.create_polygon(170, 70, 120, 170, 220, 170, fill="#00a8b5")
        logo.create_polygon(170, 110, 100, 220, 240, 220, fill="#00a8b5")

        tk.Label(center, text="VISTAVERDE", font=("Helvetica", 42, "bold"),
                 fg="white", bg="#00a8b5").pack(pady=30)
        tk.Label(center, text="Apartments", font=("Helvetica", 20), fg="#b0f8ff", bg="#00a8b5").pack()
        
        # Add database status indicator
        self.show_database_info(center)

    def show_database_info(self, parent):
        """Show database statistics on home screen"""
        try:
            conn = sqlite3.connect(DB_NAME)
            cur = conn.cursor()
            
            cur.execute("SELECT COUNT(*) FROM units WHERE is_occupied = 0")
            available = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM units WHERE is_occupied = 1")
            occupied = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM tenants")
            tenants = cur.fetchone()[0]
            
            conn.close()
            
            # Stats frame
            stats_frame = tk.Frame(parent, bg="#00a8b5")
            stats_frame.pack(pady=30)
            
            stats = [
                ("🏢", f"{available} Available Units"),
                ("🔑", f"{occupied} Occupied Units"),
                ("👥", f"{tenants} Active Tenants")
            ]
            
            for emoji, text in stats:
                stat_row = tk.Frame(stats_frame, bg="#00a8b5")
                stat_row.pack(pady=5)
                tk.Label(stat_row, text=emoji, font=("Segoe UI Emoji", 20), 
                        bg="#00a8b5").pack(side="left", padx=10)
                tk.Label(stat_row, text=text, font=("Helvetica", 14), 
                        fg="white", bg="#00a8b5").pack(side="left")
                
        except sqlite3.Error as e:
            print(f"Error loading stats: {e}")

    # ==================== PROFILE ====================
    def show_profile(self):
        self.clear_main()
        top = tk.Frame(self.main_frame, bg="#3498db", height=110)
        top.pack(fill="x"); top.pack_propagate(False)
        tk.Label(top, text=f"Welcome {self.user_data['email']}", font=("Helvetica", 20, "bold"),
                 fg="white", bg="#3498db").pack(side="left", padx=50, pady=35)

        content = tk.Frame(self.main_frame, bg="#f0f4f8")
        content.pack(fill="both", expand=True, padx=60, pady=40)

        left = tk.Frame(content, bg="white", relief="solid", bd=1, width=340)
        left.pack(side="left", padx=(0,50)); left.pack_propagate(False)
        photo = tk.Canvas(left, width=230, height=230, bg="white", highlightthickness=0)
        photo.pack(pady=50)
        photo.create_oval(20,20,210,210, fill="#e0e0e0", outline="#aaa", width=4)
        photo.create_text(115,115, text="FA", font=("Helvetica", 70, "bold"), fill="#777")
        tk.Label(left, text="Ford Asuncion", font=("Helvetica", 18, "bold"), bg="white").pack(pady=10)

        right = tk.Frame(content, bg="white", relief="solid", bd=1)
        right.pack(side="right", fill="both", expand=True)
        tk.Label(right, text="My Profile", font=("Helvetica", 22, "bold"), bg="white").pack(anchor="w", padx=50, pady=35)

        info = [
            ("Name", "First Name", self.user_data["first_name"]),
            ("Name", "Last Name", self.user_data["last_name"]),
            ("Email", "Email", self.user_data["email"]),
            ("Phone", "Phone", self.user_data["phone"]),
            ("Location", "Address", self.user_data["location"]),
        ]
        for icon, label, value in info:
            row = tk.Frame(right, bg="white")
            row.pack(fill="x", padx=60, pady=15)
            tk.Label(row, text=icon, font=("Segoe UI Emoji", 30)).pack(side="left")
            tk.Label(row, text=f"{label}:", font=("Helvetica", 12, "bold")).pack(side="left", padx=25)
            tk.Label(row, text=value, font=("Helvetica", 12), fg="#2c3e50").pack(side="left")

    # ==================== UNITS ====================
    def show_units(self):
        self.clear_main()
        top = tk.Frame(self.main_frame, bg="#2c3e50")
        top.pack(fill="x", pady=(0,15))
        tk.Label(top, text="Apartment Units", font=("Helvetica", 20, "bold"), fg="white", bg="#2c3e50")\
                 .pack(side="left", padx=20, pady=15)
        btns = tk.Frame(top, bg="#2c3e50")
        btns.pack(side="right", padx=20)
        ttk.Button(btns, text="Add Unit", command=self.add_unit).pack(side="right", padx=5)
        ttk.Button(btns, text="Delete Unit", command=self.delete_unit).pack(side="right", padx=5)

        columns = ("id", "unit_number", "unit_type", "rent", "occupied", "created")
        self.tree_units = ttk.Treeview(self.main_frame, columns=columns, show="headings")
        self.tree_units.pack(fill="both", expand=True)
        for col, text in zip(columns, ["ID", "Unit Number", "Type", "Monthly Rent", "Occupied", "Created"]):
            self.tree_units.heading(col, text=text)
            self.tree_units.column(col, anchor="center", width=150)
        self.tree_units.column("id", width=70)

        scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.tree_units.yview)
        self.tree_units.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.load_units()

    def load_units(self):
        for i in self.tree_units.get_children(): self.tree_units.delete(i)
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("SELECT * FROM units ORDER BY unit_number")
        for row in cur.fetchall():
            occupied = "Yes" if row[4] else "No"
            self.tree_units.insert("", "end", values=(row[0], row[1], row[2], f"₱{row[3]:,.2f}", occupied, row[5]))
        conn.close()

    def add_unit(self):
        AddUnitDialog(self, self.load_units)

    def delete_unit(self):
        sel = self.tree_units.selection()
        if not sel: return messagebox.showwarning("Select", "Please select a unit")
        unit_id = self.tree_units.item(sel[0])["values"][0]
        if messagebox.askyesno("Delete", "Delete this unit?"):
            conn = sqlite3.connect(DB_NAME)
            conn.execute("DELETE FROM units WHERE id=?", (unit_id,))
            conn.commit(); conn.close()
            self.load_units()

    # ==================== TENANTS ====================
    def show_tenants(self):
        self.clear_main()
        top = tk.Frame(self.main_frame, bg="#2c3e50")
        top.pack(fill="x", pady=(0,15))
        tk.Label(top, text="Tenants", font=("Helvetica", 20, "bold"), fg="white", bg="#2c3e50")\
                 .pack(side="left", padx=20, pady=15)
        btns = tk.Frame(top, bg="#2c3e50")
        btns.pack(side="right", padx=20)
        ttk.Button(btns, text="Add Tenant", command=self.add_tenant).pack(side="right", padx=5)
        ttk.Button(btns, text="Delete Tenant", command=self.delete_tenant).pack(side="right", padx=5)

        cols = ("id", "name", "email", "phone", "unit", "move_in", "rent")
        self.tree_tenants = ttk.Treeview(self.main_frame, columns=cols, show="headings")
        self.tree_tenants.pack(fill="both", expand=True)
        headings = ["ID", "Full Name", "Email", "Phone", "Unit", "Move-In", "Rent"]
        for c, h in zip(cols, headings):
            self.tree_tenants.heading(c, text=h); self.tree_tenants.column(c, anchor="center", width=160)
        self.tree_tenants.column("id", width=70)

        scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.tree_tenants.yview)
        self.tree_tenants.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.load_tenants()

    def load_tenants(self):
        for i in self.tree_tenants.get_children(): self.tree_tenants.delete(i)
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute('''
            SELECT t.id, t.full_name, t.email, t.phone, u.unit_number, t.move_in_date, t.monthly_rent
            FROM tenants t LEFT JOIN units u ON t.unit_id = u.id
        ''')
        for row in cur.fetchall():
            unit = row[4] if row[4] else "—"
            rent = f"₱{row[6]:,.2f}" if row[6] else "—"
            self.tree_tenants.insert("", "end", values=(row[0], row[1], row[2] or "—", row[3] or "—", unit, row[5], rent))
        conn.close()

    def add_tenant(self):
        AddTenantDialog(self, self.load_tenants)

    def delete_tenant(self):
        sel = self.tree_tenants.selection()
        if not sel: return messagebox.showwarning("Select", "Please select a tenant")
        tenant_id = self.tree_tenants.item(sel[0])["values"][0]
        if messagebox.askyesno("Delete", "Delete this tenant and all payments?"):
            conn = sqlite3.connect(DB_NAME)
            conn.execute("DELETE FROM tenants WHERE id=?", (tenant_id,))
            conn.commit(); conn.close()
            self.load_tenants()

    # ==================== PAYMENTS ====================
    def show_payments(self):
        self.clear_main()
        top = tk.Frame(self.main_frame, bg="#2c3e50")
        top.pack(fill="x", pady=(0,15))
        tk.Label(top, text="Payments & Due Dates", font=("Helvetica", 20, "bold"), fg="white", bg="#2c3e50")\
                 .pack(side="left", padx=20, pady=15)
        ttk.Button(top, text="Record Payment", command=self.record_payment).pack(side="right", padx=20)

        cols = ("tenant", "unit", "amount", "month", "date")
        self.tree_payments = ttk.Treeview(self.main_frame, columns=cols, show="headings")
        self.tree_payments.pack(fill="both", expand=True, padx=10, pady=10)
        headings = ["Tenant", "Unit", "Amount", "Month Covered", "Paid On"]
        for c, h in zip(cols, headings):
            self.tree_payments.heading(c, text=h); self.tree_payments.column(c, anchor="center", width=200)

        scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.tree_payments.yview)
        self.tree_payments.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.load_payments()

    def load_payments(self):
        for i in self.tree_payments.get_children(): self.tree_payments.delete(i)
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute('''
            SELECT t.full_name, u.unit_number, p.amount, p.month_covered, p.payment_date
            FROM payments p
            JOIN tenants t ON p.tenant_id = t.id
            LEFT JOIN units u ON t.unit_id = u.id
            ORDER BY p.payment_date DESC
        ''')
        for row in cur.fetchall():
            self.tree_payments.insert("", "end", values=(
                row[0], row[1] or "—", f"₱{row[2]:,.2f}", row[3], row[4]
            ))
        conn.close()

    def record_payment(self):
        RecordPaymentDialog(self, self.load_payments)

# ==================== DIALOGS ====================
class AddUnitDialog(tk.Toplevel):
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.title("Add Unit"); self.geometry("400x400"); self.resizable(False, False); self.grab_set()
        self.callback = callback
        tk.Label(self, text="Add New Unit", font=("Helvetica", 16, "bold")).pack(pady=20)
        fields = ["Unit Number (e.g. 101)", "Unit Type", "Monthly Rent (₱)"]
        self.entries = {}
        for f in fields:
            tk.Label(self, text=f + ":").pack(anchor="w", padx=50, pady=8)
            e = tk.Entry(self, width=30); e.pack(pady=5, padx=50); self.entries[f] = e
        btns = tk.Frame(self); btns.pack(pady=30)
        ttk.Button(btns, text="Add", command=self.save).pack(side="left", padx=10)
        ttk.Button(btns, text="Cancel", command=self.destroy).pack(side="left", padx=10)

    def save(self):
        num = self.entries["Unit Number (e.g. 101)"].get().strip()
        typ = self.entries["Unit Type"].get().strip()
        try: rent = float(self.entries["Monthly Rent (₱)"].get())
        except: return messagebox.showerror("Error", "Rent must be a number")
        if not num or not typ: return messagebox.showerror("Error", "All fields required")
        conn = sqlite3.connect(DB_NAME)
        try:
            conn.execute("INSERT INTO units (unit_number, unit_type, monthly_rent, created_at) VALUES (?, ?, ?, ?)",
                        (num, typ, rent, datetime.now().strftime("%Y-%m-%d")))
            conn.commit()
            messagebox.showinfo("Success", f"Unit {num} added!")
            self.callback(); self.destroy()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Unit number already exists")
        finally: conn.close()

class AddTenantDialog(tk.Toplevel):
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.title("Add Tenant"); self.geometry("500x600"); self.grab_set()
        self.callback = callback
        tk.Label(self, text="Add New Tenant", font=("Helvetica", 16, "bold")).pack(pady=20)

        self.entries = {}
        labels = ["Full Name", "Email", "Phone", "Move-In Date (YYYY-MM-DD)"]
        for l in labels:
            tk.Label(self, text=l + ":").pack(anchor="w", padx=60, pady=8)
            e = tk.Entry(self, width=40); e.pack(pady=5); self.entries[l] = e

        tk.Label(self, text="Assign to Unit:").pack(anchor="w", padx=60, pady=(20,5))
        self.unit_var = tk.StringVar()
        combo = ttk.Combobox(self, textvariable=self.unit_var, state="readonly", width=37)
        combo.pack(pady=5, padx=60)
        conn = sqlite3.connect(DB_NAME)
        units = conn.execute("SELECT id, unit_number FROM units WHERE is_occupied = 0").fetchall()
        combo['values'] = [f"{u[1]} (Available)" for u in units]
        self.unit_ids = {f"{u[1]} (Available)": u[0] for u in units}
        conn.close()

        btns = tk.Frame(self); btns.pack(pady=30)
        ttk.Button(btns, text="Add Tenant", command=self.save).pack(side="left", padx=10)
        ttk.Button(btns, text="Cancel", command=self.destroy).pack(side="left", padx=10)

    def save(self):
        name = self.entries["Full Name"].get().strip()
        email = self.entries["Email"].get().strip()
        phone = self.entries["Phone"].get().strip()
        date_in = self.entries["Move-In Date (YYYY-MM-DD)"].get().strip()
        unit_text = self.unit_var.get()
        if not name or not date_in: return messagebox.showerror("Error", "Name and Move-In Date required")

        unit_id = self.unit_ids.get(unit_text)
        conn = sqlite3.connect(DB_NAME)
        rent = conn.execute("SELECT monthly_rent FROM units WHERE id=?", (unit_id,)).fetchone()[0] if unit_id else 0
        conn.execute("INSERT INTO tenants (full_name, email, phone, unit_id, move_in_date, monthly_rent) VALUES (?, ?, ?, ?, ?, ?)",
                    (name, email or None, phone or None, unit_id, date_in, rent))
        if unit_id:
            conn.execute("UPDATE units SET is_occupied = 1 WHERE id=?", (unit_id,))
        conn.commit(); conn.close()
        messagebox.showinfo("Success", f"Tenant {name} added!")
        self.callback(); self.destroy()

class RecordPaymentDialog(tk.Toplevel):
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.title("Record Payment"); self.geometry("450x400"); self.grab_set()
        self.callback = callback
        tk.Label(self, text="Record Payment", font=("Helvetica", 16, "bold")).pack(pady=20)

        tk.Label(self, text="Select Tenant:").pack(anchor="w", padx=60, pady=(10,5))
        self.tenant_var = tk.StringVar()
        combo = ttk.Combobox(self, textvariable=self.tenant_var, state="readonly", width=40)
        combo.pack(pady=5, padx=60)
        conn = sqlite3.connect(DB_NAME)
        tenants = conn.execute("SELECT id, full_name FROM tenants").fetchall()
        combo['values'] = [t[1] for t in tenants]
        self.tenant_ids = {t[1]: t[0] for t in tenants}
        conn.close()

        tk.Label(self, text="Amount Paid (₱):").pack(anchor="w", padx=60, pady=(15,5))
        self.amount_entry = tk.Entry(self, width=30); self.amount_entry.pack(pady=5)

        tk.Label(self, text="Month Covered (e.g. 2025-12):").pack(anchor="w", padx=60, pady=(15,5))
        self.month_entry = tk.Entry(self, width=30); self.month_entry.pack(pady=5)
        self.month_entry.insert(0, datetime.now().strftime("%Y-%m"))

        btns = tk.Frame(self); btns.pack(pady=30)
        ttk.Button(btns, text="Record Payment", command=self.save).pack(side="left", padx=10)
        ttk.Button(btns, text="Cancel", command=self.destroy).pack(side="left", padx=10)

    def save(self):
        tenant_name = self.tenant_var.get()
        try: amount = float(self.amount_entry.get())
        except: return messagebox.showerror("Error", "Invalid amount")
        month = self.month_entry.get().strip()
        if not tenant_name or not month: return messagebox.showerror("Error", "All fields required")

        tenant_id = self.tenant_ids[tenant_name]
        conn = sqlite3.connect(DB_NAME)
        conn.execute("INSERT INTO payments (tenant_id, amount, payment_date, month_covered) VALUES (?, ?, ?, ?)",
                    (tenant_id, amount, datetime.now().strftime("%Y-%m-%d"), month))
        conn.commit(); conn.close()
        messagebox.showinfo("Success", f"Payment of ₱{amount:,.2f} recorded!")
        self.callback(); self.destroy()

# ==================== RUN ====================
if __name__ == "__main__":
    print("\n" + "="*50)
    print("🏢 Vista Verde Apartments RMS")
    print("="*50)
    app = VistaVerdeApp()
    app.mainloop()
