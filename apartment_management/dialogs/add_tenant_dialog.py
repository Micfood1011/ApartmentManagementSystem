#!/usr/bin/env python3
"""Add Tenant Dialog"""
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

DB_NAME = "vista_verde.db"

class AddTenantDialog(tk.Toplevel):
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.title("Add Tenant")
        self.geometry("500x600")
        self.grab_set()
        self.callback = callback
        
        tk.Label(self, text="Add New Tenant", font=("Helvetica", 16, "bold")).pack(pady=20)

        self.entries = {}
        labels = ["Full Name", "Email", "Phone", "Move-In Date (YYYY-MM-DD)"]
        for l in labels:
            tk.Label(self, text=l + ":").pack(anchor="w", padx=60, pady=8)
            e = tk.Entry(self, width=40)
            e.pack(pady=5)
            self.entries[l] = e

        tk.Label(self, text="Assign to Unit:").pack(anchor="w", padx=60, pady=(20,5))
        self.unit_var = tk.StringVar()
        combo = ttk.Combobox(self, textvariable=self.unit_var, state="readonly", width=37)
        combo.pack(pady=5, padx=60)
        
        conn = sqlite3.connect(DB_NAME)
        units = conn.execute("SELECT id, unit_number FROM units WHERE is_occupied = 0").fetchall()
        combo['values'] = [f"{u[1]} (Available)" for u in units]
        self.unit_ids = {f"{u[1]} (Available)": u[0] for u in units}
        conn.close()

        btns = tk.Frame(self)
        btns.pack(pady=30)
        ttk.Button(btns, text="Add Tenant", command=self.save).pack(side="left", padx=10)
        ttk.Button(btns, text="Cancel", command=self.destroy).pack(side="left", padx=10)

    def save(self):
        name = self.entries["Full Name"].get().strip()
        email = self.entries["Email"].get().strip()
        phone = self.entries["Phone"].get().strip()
        date_in = self.entries["Move-In Date (YYYY-MM-DD)"].get().strip()
        unit_text = self.unit_var.get()
        
        if not name or not date_in:
            return messagebox.showerror("Error", "Name and Move-In Date required")

        unit_id = self.unit_ids.get(unit_text)
        conn = sqlite3.connect(DB_NAME)
        rent = conn.execute("SELECT monthly_rent FROM units WHERE id=?",
                          (unit_id,)).fetchone()[0] if unit_id else 0
        conn.execute("INSERT INTO tenants (full_name, email, phone, unit_id, move_in_date, monthly_rent) VALUES (?, ?, ?, ?, ?, ?)",
                    (name, email or None, phone or None, unit_id, date_in, rent))
        if unit_id:
            conn.execute("UPDATE units SET is_occupied = 1 WHERE id=?", (unit_id,))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", f"Tenant {name} added!")
        self.callback()
        self.destroy()