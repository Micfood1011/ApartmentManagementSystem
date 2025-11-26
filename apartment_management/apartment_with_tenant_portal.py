#!/usr/bin/env python3
"""
apartment_with_tenant_portal.py

Adds a Tenant Portal tab (Tenant self-registration popup) to the Apartment Management System.
This is a standalone file based on the previously provided app and the uploaded spec:
/mnt/data/OOP_Apartment Management System(1).pdf. :contentReference[oaicite:1]{index=1}

How to use:
    python apartment_with_tenant_portal.py

This creates/uses apartment.db in the same folder.
"""
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, datetime

DB_FILENAME = "apartment.db"

# ---------------------------
# Database Layer (OOP wrapper)
# ---------------------------
class Database:
    def __init__(self, db_filename=DB_FILENAME):
        self.conn = sqlite3.connect(db_filename)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        cur = self.conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS units (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                unit_number TEXT NOT NULL UNIQUE,
                unit_type TEXT,
                monthly_rent REAL,
                is_occupied INTEGER DEFAULT 0,
                created_at TEXT
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS tenants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                contact TEXT,
                email TEXT,
                unit_id INTEGER,
                lease_start TEXT,
                lease_end TEXT,
                created_at TEXT,
                FOREIGN KEY(unit_id) REFERENCES units(id)
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id INTEGER,
                amount REAL,
                payment_date TEXT,
                payment_month TEXT,
                status TEXT,
                created_at TEXT,
                FOREIGN KEY(tenant_id) REFERENCES tenants(id)
            )
        """)
        self.conn.commit()

    # Units
    def add_unit(self, unit_number, unit_type, monthly_rent):
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO units (unit_number, unit_type, monthly_rent, is_occupied, created_at) VALUES (?, ?, ?, 0, ?)",
            (unit_number, unit_type, monthly_rent, datetime.utcnow().isoformat())
        )
        self.conn.commit()
        return cur.lastrowid

    def delete_unit(self, unit_id):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM units WHERE id = ?", (unit_id,))
        self.conn.commit()

    def get_units(self):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM units ORDER BY id")
        return cur.fetchall()

    def get_available_units(self):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM units WHERE is_occupied = 0 ORDER BY id")
        return cur.fetchall()

    def set_unit_occupied(self, unit_id, occupied=True):
        cur = self.conn.cursor()
        cur.execute("UPDATE units SET is_occupied = ? WHERE id = ?", (1 if occupied else 0, unit_id))
        self.conn.commit()

    def get_unit(self, unit_id):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM units WHERE id = ?", (unit_id,))
        return cur.fetchone()

    # Tenants
    def add_tenant(self, name, contact, email, unit_id, lease_start, lease_end):
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO tenants (name, contact, email, unit_id, lease_start, lease_end, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (name, contact, email, unit_id, lease_start, lease_end, datetime.utcnow().isoformat()))
        self.conn.commit()
        return cur.lastrowid

    def remove_tenant(self, tenant_id):
        tenant = self.get_tenant(tenant_id)
        if tenant and tenant["unit_id"]:
            self.set_unit_occupied(tenant["unit_id"], False)
        cur = self.conn.cursor()
        cur.execute("DELETE FROM tenants WHERE id = ?", (tenant_id,))
        self.conn.commit()

    def get_tenants(self):
        cur = self.conn.cursor()
        cur.execute("""
            SELECT tenants.*, units.unit_number, units.unit_type
            FROM tenants
            LEFT JOIN units ON tenants.unit_id = units.id
            ORDER BY tenants.id
        """)
        return cur.fetchall()

    def get_tenant(self, tenant_id):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM tenants WHERE id = ?", (tenant_id,))
        return cur.fetchone()

    # Payments
    def add_payment(self, tenant_id, amount, payment_month, status="Paid"):
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO payments (tenant_id, amount, payment_date, payment_month, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (tenant_id, amount, datetime.utcnow().date().isoformat(), payment_month, status, datetime.utcnow().isoformat()))
        self.conn.commit()
        return cur.lastrowid

    def get_payments(self):
        cur = self.conn.cursor()
        cur.execute("""
            SELECT payments.*, tenants.name as tenant_name, tenants.unit_id
            FROM payments
            LEFT JOIN tenants ON payments.tenant_id = tenants.id
            ORDER BY payments.id DESC
        """)
        return cur.fetchall()

    def get_payments_for_tenant(self, tenant_id):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM payments WHERE tenant_id = ? ORDER BY id DESC", (tenant_id,))
        return cur.fetchall()

    def get_total_paid_by_tenant(self, tenant_id):
        cur = self.conn.cursor()
        cur.execute("SELECT SUM(amount) as total FROM payments WHERE tenant_id = ?", (tenant_id,))
        row = cur.fetchone()
        return row["total"] if row and row["total"] is not None else 0.0

# ---------------------------
# GUI Layer (Tkinter)
# ---------------------------
class ApartmentApp(tk.Tk):
    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self.title("Apartment Management System")
        self.geometry("1000x620")
        self.minsize(900, 540)

        # Notebook (tabs)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Create tabs
        self.units_frame = ttk.Frame(self.notebook)
        self.tenants_frame = ttk.Frame(self.notebook)
        self.payments_frame = ttk.Frame(self.notebook)
        self.tenant_portal_frame = ttk.Frame(self.notebook)  # NEW tab

        self.notebook.add(self.units_frame, text="Units")
        self.notebook.add(self.tenants_frame, text="Tenants")
        self.notebook.add(self.payments_frame, text="Payments")
        self.notebook.add(self.tenant_portal_frame, text="Tenant Portal")  # add tab

        # Build each tab
        self._build_units_tab()
        self._build_tenants_tab()
        self._build_payments_tab()
        self._build_tenant_portal_tab()  # NEW

        # Load initial data
        self.refresh_units()
        self.refresh_tenants()
        self.refresh_payments()
        self.refresh_tenant_portal_units()

    # ---------------- Units Tab ----------------
    def _build_units_tab(self):
        top = ttk.Frame(self.units_frame)
        top.pack(fill="x", padx=8, pady=8)

        lbl = ttk.Label(top, text="Apartment Units", font=("Segoe UI", 14, "bold"))
        lbl.pack(side="left", padx=(2, 8))

        add_btn = ttk.Button(top, text="Add Unit", command=self.open_add_unit_dialog)
        add_btn.pack(side="right", padx=4)
        del_btn = ttk.Button(top, text="Delete Unit", command=self.delete_selected_unit)
        del_btn.pack(side="right", padx=4)

        cols = ("id", "unit_number", "unit_type", "monthly_rent", "is_occupied", "created_at")
        self.units_tree = ttk.Treeview(self.units_frame, columns=cols, show="headings", height=15)
        for c in cols:
            heading = c.replace("_", " ").title()
            self.units_tree.heading(c, text=heading)
            if c == "unit_number":
                self.units_tree.column(c, width=120)
            elif c == "unit_type":
                self.units_tree.column(c, width=150)
            elif c == "monthly_rent":
                self.units_tree.column(c, width=120, anchor="e")
            elif c == "is_occupied":
                self.units_tree.column(c, width=100, anchor="center")
            else:
                self.units_tree.column(c, width=140)
        self.units_tree.pack(fill="both", expand=True, padx=8, pady=(0, 8))

    def refresh_units(self):
        for r in self.units_tree.get_children():
            self.units_tree.delete(r)
        for u in self.db.get_units():
            self.units_tree.insert("", "end", values=(
                u["id"], u["unit_number"], u["unit_type"],
                f"₱{u['monthly_rent']:.2f}" if u["monthly_rent"] is not None else "",
                "Yes" if u["is_occupied"] else "No",
                u["created_at"][:19] if u["created_at"] else ""
            ))

    def open_add_unit_dialog(self):
        dlg = AddUnitDialog(self, self.db)
        self.wait_window(dlg)
        self.refresh_units()
        self.refresh_tenant_portal_units()

    def delete_selected_unit(self):
        sel = self.units_tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Please select a unit to delete.")
            return
        item = self.units_tree.item(sel[0])
        unit_id = item["values"][0]
        is_occupied = item["values"][4] == "Yes"
        if is_occupied:
            messagebox.showwarning("Warning", "Cannot delete occupied unit. Remove tenant first.")
            return
        if messagebox.askyesno("Confirm", "Are you sure you want to delete the selected unit?"):
            self.db.delete_unit(unit_id)
            self.refresh_units()
            self.refresh_tenant_portal_units()

    # ---------------- Tenants Tab ----------------
    def _build_tenants_tab(self):
        top = ttk.Frame(self.tenants_frame)
        top.pack(fill="x", padx=8, pady=8)

        lbl = ttk.Label(top, text="Tenants", font=("Segoe UI", 14, "bold"))
        lbl.pack(side="left", padx=(2, 8))

        add_btn = ttk.Button(top, text="Register Tenant", command=self.open_register_tenant_dialog)
        add_btn.pack(side="right", padx=4)
        del_btn = ttk.Button(top, text="Remove Tenant", command=self.remove_selected_tenant)
        del_btn.pack(side="right", padx=4)
        view_pay_btn = ttk.Button(top, text="View Payments", command=self.view_selected_tenant_payments)
        view_pay_btn.pack(side="right", padx=4)

        cols = ("id", "name", "contact", "email", "unit_number", "lease_end", "created_at")
        self.tenants_tree = ttk.Treeview(self.tenants_frame, columns=cols, show="headings", height=15)
        for c in cols:
            heading = c.replace("_", " ").title()
            self.tenants_tree.heading(c, text=heading)
            if c == "name":
                self.tenants_tree.column(c, width=180)
            elif c == "unit_number":
                self.tenants_tree.column(c, width=120, anchor="center")
            else:
                self.tenants_tree.column(c, width=140)
        self.tenants_tree.pack(fill="both", expand=True, padx=8, pady=(0, 8))

    def refresh_tenants(self):
        for r in self.tenants_tree.get_children():
            self.tenants_tree.delete(r)
        for t in self.db.get_tenants():
            self.tenants_tree.insert("", "end", values=(
                t["id"], t["name"], t["contact"], t["email"],
                t["unit_number"] if t["unit_number"] else "N/A",
                t["lease_end"] if t["lease_end"] else "",
                t["created_at"][:19] if t["created_at"] else ""
            ))

    def open_register_tenant_dialog(self):
        dlg = RegisterTenantDialog(self, self.db)
        self.wait_window(dlg)
        self.refresh_tenants()
        self.refresh_units()
        self.refresh_payments()
        self.refresh_tenant_portal_units()

    def remove_selected_tenant(self):
        sel = self.tenants_tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Please select a tenant to remove.")
            return
        item = self.tenants_tree.item(sel[0])
        tenant_id = item["values"][0]
        if messagebox.askyesno("Confirm", "Remove tenant? This will free the unit too."):
            self.db.remove_tenant(tenant_id)
            self.refresh_tenants()
            self.refresh_units()
            self.refresh_payments()
            self.refresh_tenant_portal_units()

    def view_selected_tenant_payments(self):
        sel = self.tenants_tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Please select a tenant to view payments.")
            return
        item = self.tenants_tree.item(sel[0])
        tenant_id = item["values"][0]
        dlg = TenantPaymentsDialog(self, self.db, tenant_id)
        self.wait_window(dlg)

    # ---------------- Payments Tab ----------------
    def _build_payments_tab(self):
        top = ttk.Frame(self.payments_frame)
        top.pack(fill="x", padx=8, pady=8)

        lbl = ttk.Label(top, text="Payments", font=("Segoe UI", 14, "bold"))
        lbl.pack(side="left", padx=(2, 8))

        add_btn = ttk.Button(top, text="Record Payment", command=self.open_record_payment_dialog)
        add_btn.pack(side="right", padx=4)

        cols = ("id", "payment_date", "tenant_name", "amount", "payment_month", "status")
        self.payments_tree = ttk.Treeview(self.payments_frame, columns=cols, show="headings", height=18)
        for c in cols:
            heading = c.replace("_", " ").title()
            self.payments_tree.heading(c, text=heading)
            if c == "tenant_name":
                self.payments_tree.column(c, width=200)
            elif c == "amount":
                self.payments_tree.column(c, width=120, anchor="e")
            else:
                self.payments_tree.column(c, width=140)
        self.payments_tree.pack(fill="both", expand=True, padx=8, pady=(0, 8))

    def refresh_payments(self):
        for r in self.payments_tree.get_children():
            self.payments_tree.delete(r)
        for p in self.db.get_payments():
            tenant_name = p["tenant_name"] if p["tenant_name"] else "Unknown"
            self.payments_tree.insert("", "end", values=(
                p["id"], p["payment_date"], tenant_name,
                f"₱{p['amount']:.2f}", p["payment_month"], p["status"]
            ))

    def open_record_payment_dialog(self):
        dlg = RecordPaymentDialog(self, self.db)
        self.wait_window(dlg)
        self.refresh_payments()
        self.refresh_tenants()

    # ---------------- Tenant Portal Tab (NEW) ----------------
    def _build_tenant_portal_tab(self):
        top = ttk.Frame(self.tenant_portal_frame)
        top.pack(fill="x", padx=8, pady=8)

        lbl = ttk.Label(top, text="Tenant Self-Registration Portal", font=("Segoe UI", 14, "bold"))
        lbl.pack(side="left", padx=(2, 8))

        instr = ttk.Label(top, text="Select an available unit below then click 'Register for Selected Unit' to apply.")
        instr.pack(fill="x", padx=8, pady=(6, 0))

        # Units table (available only)
        cols = ("id", "unit_number", "unit_type", "monthly_rent")
        self.portal_units_tree = ttk.Treeview(self.tenant_portal_frame, columns=cols, show="headings", height=12)
        for c in cols:
            self.portal_units_tree.heading(c, text=c.replace("_", " ").title())
            if c == "unit_number":
                self.portal_units_tree.column(c, width=120)
            elif c == "monthly_rent":
                self.portal_units_tree.column(c, width=140, anchor="e")
            else:
                self.portal_units_tree.column(c, width=180)
        self.portal_units_tree.pack(fill="both", expand=True, padx=8, pady=(6, 8))

        # Buttons
        btn_frame = ttk.Frame(self.tenant_portal_frame)
        btn_frame.pack(fill="x", padx=8, pady=(0, 8))
        self.register_for_unit_btn = ttk.Button(btn_frame, text="Register for Selected Unit", command=self.open_tenant_portal_register_popup, state="disabled")
        self.register_for_unit_btn.pack(side="right")

        refresh_btn = ttk.Button(btn_frame, text="Refresh List", command=self.refresh_tenant_portal_units)
        refresh_btn.pack(side="right", padx=(0, 6))

        # Enable button when selection changes
        self.portal_units_tree.bind("<<TreeviewSelect>>", self._on_portal_unit_select)

    def refresh_tenant_portal_units(self):
        for r in self.portal_units_tree.get_children():
            self.portal_units_tree.delete(r)
        for u in self.db.get_available_units():
            self.portal_units_tree.insert("", "end", values=(
                u["id"], f"Unit {u['unit_number']}", u["unit_type"], f"₱{u['monthly_rent']:.2f}"
            ))
        # disable register button until a selection is made
        self.register_for_unit_btn.config(state="disabled")

    def _on_portal_unit_select(self, _evt):
        sel = self.portal_units_tree.selection()
        if sel:
            self.register_for_unit_btn.config(state="normal")
        else:
            self.register_for_unit_btn.config(state="disabled")

    def open_tenant_portal_register_popup(self):
        sel = self.portal_units_tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Please select an available unit first.")
            return
        item = self.portal_units_tree.item(sel[0])
        unit_id = item["values"][0]
        unit_label = item["values"][1]
        dlg = TenantPortalRegisterDialog(self, self.db, unit_id, unit_label)
        self.wait_window(dlg)
        # refresh everything after registration (units, tenants, payments, portal list)
        self.refresh_tenant_portal_units()
        self.refresh_units()
        self.refresh_tenants()
        self.refresh_payments()

# ---------------------------
# Dialogs (Add/Edit/Register/Payments)
# ---------------------------
class AddUnitDialog(tk.Toplevel):
    def __init__(self, parent, db: Database):
        super().__init__(parent)
        self.db = db
        self.title("Add New Unit")
        self.resizable(False, False)
        self.grab_set()

        frm = ttk.Frame(self, padding=12)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text="Unit Number").grid(row=0, column=0, sticky="w")
        self.unit_number = ttk.Entry(frm)
        self.unit_number.grid(row=0, column=1, pady=6, sticky="ew")

        ttk.Label(frm, text="Unit Type").grid(row=1, column=0, sticky="w")
        self.unit_type = ttk.Entry(frm)
        self.unit_type.grid(row=1, column=1, pady=6, sticky="ew")

        ttk.Label(frm, text="Monthly Rent (₱)").grid(row=2, column=0, sticky="w")
        self.monthly_rent = ttk.Entry(frm)
        self.monthly_rent.grid(row=2, column=1, pady=6, sticky="ew")

        frm.columnconfigure(1, weight=1)

        btns = ttk.Frame(frm)
        btns.grid(row=3, column=0, columnspan=2, pady=(10,0))
        ttk.Button(btns, text="Add", command=self.on_add).pack(side="left", padx=4)
        ttk.Button(btns, text="Cancel", command=self.destroy).pack(side="left", padx=4)

    def on_add(self):
        num = self.unit_number.get().strip()
        utype = self.unit_type.get().strip()
        rent = self.monthly_rent.get().strip()
        if not num or not utype or not rent:
            messagebox.showwarning("Validation", "Please fill all fields.")
            return
        try:
            rent_val = float(rent)
        except ValueError:
            messagebox.showwarning("Validation", "Monthly rent must be a number.")
            return
        try:
            self.db.add_unit(num, utype, rent_val)
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Unit number already exists.")
            return
        messagebox.showinfo("Success", "Unit added.")
        self.destroy()

class RegisterTenantDialog(tk.Toplevel):
    def __init__(self, parent, db: Database):
        super().__init__(parent)
        self.db = db
        self.title("Register Tenant (Admin)")
        self.resizable(False, False)
        self.grab_set()

        frm = ttk.Frame(self, padding=12)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text="Tenant Name").grid(row=0, column=0, sticky="w")
        self.name = ttk.Entry(frm)
        self.name.grid(row=0, column=1, pady=6, sticky="ew")

        ttk.Label(frm, text="Contact Number").grid(row=1, column=0, sticky="w")
        self.contact = ttk.Entry(frm)
        self.contact.grid(row=1, column=1, pady=6, sticky="ew")

        ttk.Label(frm, text="Email Address").grid(row=2, column=0, sticky="w")
        self.email = ttk.Entry(frm)
        self.email.grid(row=2, column=1, pady=6, sticky="ew")

        ttk.Label(frm, text="Unit (only available)").grid(row=3, column=0, sticky="w")
        self.unit_combo = ttk.Combobox(frm, state="readonly")
        self.unit_combo.grid(row=3, column=1, pady=6, sticky="ew")

        ttk.Label(frm, text="Lease Duration (months)").grid(row=4, column=0, sticky="w")
        self.lease_months = ttk.Entry(frm)
        self.lease_months.insert(0, "12")
        self.lease_months.grid(row=4, column=1, pady=6, sticky="ew")

        frm.columnconfigure(1, weight=1)

        btns = ttk.Frame(frm)
        btns.grid(row=5, column=0, columnspan=2, pady=(10,0))
        ttk.Button(btns, text="Register", command=self.on_register).pack(side="left", padx=4)
        ttk.Button(btns, text="Cancel", command=self.destroy).pack(side="left", padx=4)

        self.populate_units()

    def populate_units(self):
        units = [u for u in self.db.get_units() if u["is_occupied"] == 0]
        display = [f"{u['id']} - Unit {u['unit_number']} ({u['unit_type']}) ₱{u['monthly_rent']:.2f}" for u in units]
        self.unit_mapping = {display[i]: units[i]["id"] for i in range(len(units))}
        self.unit_combo["values"] = display
        if display:
            self.unit_combo.current(0)

    def on_register(self):
        name = self.name.get().strip()
        contact = self.contact.get().strip()
        email = self.email.get().strip()
        unit_display = self.unit_combo.get().strip()
        lease_months = self.lease_months.get().strip() or "12"

        if not name or not unit_display:
            messagebox.showwarning("Validation", "Please fill name and choose a unit.")
            return
        try:
            months = int(lease_months)
            if months <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showwarning("Validation", "Lease months must be a positive integer.")
            return

        unit_id = self.unit_mapping.get(unit_display)
        if unit_id is None:
            messagebox.showerror("Error", "Selected unit invalid.")
            return

        start = date.today()
        year = start.year + (start.month - 1 + months) // 12
        month = (start.month - 1 + months) % 12 + 1
        day = min(start.day, 28)
        end = date(year, month, day)

        tenant_id = self.db.add_tenant(name, contact, email, unit_id, start.isoformat(), end.isoformat())
        self.db.set_unit_occupied(unit_id, True)
        messagebox.showinfo("Success", f"Tenant registered with ID {tenant_id}. Lease ends {end.isoformat()}")
        self.destroy()

class TenantPortalRegisterDialog(tk.Toplevel):
    """
    Popup shown when tenant selects a unit in Tenant Portal and wants to register.
    """
    def __init__(self, parent, db: Database, unit_id: int, unit_label: str):
        super().__init__(parent)
        self.db = db
        self.unit_id = unit_id
        self.unit_label = unit_label
        self.title(f"Register for {unit_label}")
        self.resizable(False, False)
        self.grab_set()

        frm = ttk.Frame(self, padding=12)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text=f"Registering for: {unit_label}", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0,8))

        ttk.Label(frm, text="Your Full Name").grid(row=1, column=0, sticky="w")
        self.name = ttk.Entry(frm)
        self.name.grid(row=1, column=1, pady=6, sticky="ew")

        ttk.Label(frm, text="Contact Number").grid(row=2, column=0, sticky="w")
        self.contact = ttk.Entry(frm)
        self.contact.grid(row=2, column=1, pady=6, sticky="ew")

        ttk.Label(frm, text="Email Address").grid(row=3, column=0, sticky="w")
        self.email = ttk.Entry(frm)
        self.email.grid(row=3, column=1, pady=6, sticky="ew")

        ttk.Label(frm, text="Lease Duration (months)").grid(row=4, column=0, sticky="w")
        self.lease_months = ttk.Entry(frm)
        self.lease_months.insert(0, "12")
        self.lease_months.grid(row=4, column=1, pady=6, sticky="ew")

        frm.columnconfigure(1, weight=1)

        btns = ttk.Frame(frm)
        btns.grid(row=5, column=0, columnspan=2, pady=(10,0))
        ttk.Button(btns, text="Submit Registration", command=self.on_submit).pack(side="left", padx=4)
        ttk.Button(btns, text="Cancel", command=self.destroy).pack(side="left", padx=4)

    def on_submit(self):
        name = self.name.get().strip()
        contact = self.contact.get().strip()
        email = self.email.get().strip()
        lease_months = self.lease_months.get().strip() or "12"

        if not name:
            messagebox.showwarning("Validation", "Please fill your name.")
            return
        try:
            months = int(lease_months)
            if months <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showwarning("Validation", "Lease months must be a positive integer.")
            return

        # Check unit availability again (race-safe-ish)
        unit = self.db.get_unit(self.unit_id)
        if not unit:
            messagebox.showerror("Error", "Unit not found.")
            return
        if unit["is_occupied"]:
            messagebox.showwarning("Unavailable", "Sorry — this unit was just taken. Please pick another unit.")
            self.destroy()
            return

        start = date.today()
        year = start.year + (start.month - 1 + months) // 12
        month = (start.month - 1 + months) % 12 + 1
        day = min(start.day, 28)
        end = date(year, month, day)

        tenant_id = self.db.add_tenant(name, contact, email, self.unit_id, start.isoformat(), end.isoformat())
        self.db.set_unit_occupied(self.unit_id, True)
        messagebox.showinfo("Success", f"Thank you {name}! Your registration was successful.\nTenant ID: {tenant_id}\nLease end: {end.isoformat()}")
        self.destroy()

class RecordPaymentDialog(tk.Toplevel):
    def __init__(self, parent, db: Database):
        super().__init__(parent)
        self.db = db
        self.title("Record Payment")
        self.resizable(False, False)
        self.grab_set()

        frm = ttk.Frame(self, padding=12)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text="Tenant").grid(row=0, column=0, sticky="w")
        self.tenant_combo = ttk.Combobox(frm, state="readonly")
        self.tenant_combo.grid(row=0, column=1, pady=6, sticky="ew")

        ttk.Label(frm, text="Amount (₱)").grid(row=1, column=0, sticky="w")
        self.amount = ttk.Entry(frm)
        self.amount.grid(row=1, column=1, pady=6, sticky="ew")

        ttk.Label(frm, text="Payment Month (e.g., January 2025)").grid(row=2, column=0, sticky="w")
        self.payment_month = ttk.Entry(frm)
        self.payment_month.grid(row=2, column=1, pady=6, sticky="ew")

        frm.columnconfigure(1, weight=1)

        btns = ttk.Frame(frm)
        btns.grid(row=3, column=0, columnspan=2, pady=(10,0))
        ttk.Button(btns, text="Record", command=self.on_record).pack(side="left", padx=4)
        ttk.Button(btns, text="Cancel", command=self.destroy).pack(side="left", padx=4)

        self.populate_tenants()

    def populate_tenants(self):
        tenants = self.db.get_tenants()
        display = [f"{t['id']} - {t['name']} (Unit {t['unit_number'] if t['unit_number'] else 'N/A'})" for t in tenants]
        self.tenant_mapping = {display[i]: tenants[i]["id"] for i in range(len(tenants))}
        self.tenant_combo["values"] = display
        if display:
            self.tenant_combo.current(0)

    def on_record(self):
        tenant_display = self.tenant_combo.get().strip()
        amount = self.amount.get().strip()
        payment_month = self.payment_month.get().strip()

        if not tenant_display or not amount or not payment_month:
            messagebox.showwarning("Validation", "Fill all fields.")
            return
        try:
            amount_val = float(amount)
            if amount_val <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showwarning("Validation", "Amount must be a positive number.")
            return
        tenant_id = self.tenant_mapping.get(tenant_display)
        if tenant_id is None:
            messagebox.showerror("Error", "Invalid tenant selected.")
            return

        self.db.add_payment(tenant_id, amount_val, payment_month, status="Paid")
        messagebox.showinfo("Success", "Payment recorded.")
        self.destroy()

class TenantPaymentsDialog(tk.Toplevel):
    def __init__(self, parent, db: Database, tenant_id: int):
        super().__init__(parent)
        self.db = db
        self.title("Tenant Payments")
        self.resizable(True, True)
        self.geometry("500x400")
        self.grab_set()

        tenant = self.db.get_tenant(tenant_id)
        name = tenant["name"] if tenant else "Unknown"
        ttk.Label(self, text=f"Payment History - {name}", font=("Segoe UI", 12, "bold")).pack(pady=8)

        frame = ttk.Frame(self, padding=8)
        frame.pack(fill="both", expand=True)

        cols = ("payment_date", "amount", "payment_month", "status")
        tree = ttk.Treeview(frame, columns=cols, show="headings")
        for c in cols:
            tree.heading(c, text=c.replace("_", " ").title())
            tree.column(c, width=120)
        tree.pack(fill="both", expand=True)

        for p in self.db.get_payments_for_tenant(tenant_id):
            tree.insert("", "end", values=(p["payment_date"], f"₱{p['amount']:.2f}", p["payment_month"], p["status"]))

        total = self.db.get_total_paid_by_tenant(tenant_id)
        ttk.Label(self, text=f"Total Paid: ₱{total:.2f}", font=("Segoe UI", 10, "bold")).pack(pady=8)

        ttk.Button(self, text="Close", command=self.destroy).pack(pady=(0, 8))

# ---------------------------
# Main entry point
# ---------------------------
def main():
    db = Database()
    app = ApartmentApp(db)
    app.mainloop()

if __name__ == "__main__":
    main()
