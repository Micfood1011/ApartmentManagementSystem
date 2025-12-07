#!/usr/bin/env python3
"""Record Payment Dialog"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import sqlite3

DB_NAME = "vista_verde.db"

class RecordPaymentDialog(tk.Toplevel):
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.title("Record Payment")
        self.geometry("450x400")
        self.grab_set()
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
        self.amount_entry = tk.Entry(self, width=30)
        self.amount_entry.pack(pady=5)

        tk.Label(self, text="Month Covered (e.g. 2025-12):").pack(anchor="w", padx=60, pady=(15,5))
        self.month_entry = tk.Entry(self, width=30)
        self.month_entry.pack(pady=5)
        self.month_entry.insert(0, datetime.now().strftime("%Y-%m"))

        btns = tk.Frame(self)
        btns.pack(pady=30)
        ttk.Button(btns, text="Record Payment", command=self.save).pack(side="left", padx=10)
        ttk.Button(btns, text="Cancel", command=self.destroy).pack(side="left", padx=10)

    def save(self):
        tenant_name = self.tenant_var.get()
        try:
            amount = float(self.amount_entry.get())
        except:
            return messagebox.showerror("Error", "Invalid amount")
        month = self.month_entry.get().strip()
        
        if not tenant_name or not month:
            return messagebox.showerror("Error", "All fields required")

        tenant_id = self.tenant_ids[tenant_name]
        conn = sqlite3.connect(DB_NAME)
        conn.execute("INSERT INTO payments (tenant_id, amount, payment_date, month_covered) VALUES (?, ?, ?, ?)",
                    (tenant_id, amount, datetime.now().strftime("%Y-%m-%d"), month))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", f"Payment of ₱{amount:,.2f} recorded!")
        self.callback()
        self.destroy()