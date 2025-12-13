#!/usr/bin/env python3
"""
Vista Verde Apartments - Payments Page Module
"""
import tkinter as tk
from tkinter import ttk
import sqlite3
from dialogs.record_payment_dialog import RecordPaymentDialog

DB_NAME = "vista_verde.db"

class PaymentsPage:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.tree_payments = None

    def show(self):
        # Header
        top = tk.Frame(self.parent, bg="#2c3e50")
        top.pack(fill="x", pady=(0,15))
        tk.Label(top, text="Payments & Due Dates", font=("Helvetica", 20, "bold"),
                fg="white", bg="#2c3e50").pack(side="left", padx=20, pady=15)
        
        # Button
        ttk.Button(top, text="Record Payment", 
                  command=self.record_payment).pack(side="right", padx=20)

        # Treeview
        cols = ("tenant", "unit", "amount", "month", "date")
        self.tree_payments = ttk.Treeview(self.parent, columns=cols, show="headings")
        self.tree_payments.pack(fill="both", expand=True, padx=10, pady=10)
        
        headings = ["Tenant", "Unit", "Amount", "Month Covered", "Paid On"]
        for c, h in zip(cols, headings):
            self.tree_payments.heading(c, text=h)
            self.tree_payments.column(c, anchor="center", width=200)

        # Scrollbar
        scrollbar = ttk.Scrollbar(self.parent, orient="vertical", command=self.tree_payments.yview)
        self.tree_payments.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        
        self.load_payments()

    def load_payments(self):
        if not self.tree_payments:
            return
        for i in self.tree_payments.get_children():
            self.tree_payments.delete(i)
        
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
        RecordPaymentDialog(self.app, self.load_payments)
