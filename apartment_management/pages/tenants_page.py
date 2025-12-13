#!/usr/bin/env python3
"""
Vista Verde Apartments - Tenants Page Module
"""
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from dialogs.add_tenant_dialog import AddTenantDialog

DB_NAME = "vista_verde.db"

class TenantsPage:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.tree_tenants = None

    def show(self):
        # Header
        top = tk.Frame(self.parent, bg="#2c3e50")
        top.pack(fill="x", pady=(0,15))
        tk.Label(top, text="Tenants", font=("Helvetica", 20, "bold"),
                fg="white", bg="#2c3e50").pack(side="left", padx=20, pady=15)
        
        # Buttons
        btns = tk.Frame(top, bg="#2c3e50")
        btns.pack(side="right", padx=20)
        ttk.Button(btns, text="Add Tenant", command=self.add_tenant).pack(side="right", padx=5)
        ttk.Button(btns, text="Delete Tenant", command=self.delete_tenant).pack(side="right", padx=5)

        # Treeview
        cols = ("id", "name", "email", "phone", "unit", "move_in", "rent")
        self.tree_tenants = ttk.Treeview(self.parent, columns=cols, show="headings")
        self.tree_tenants.pack(fill="both", expand=True)
        
        headings = ["ID", "Full Name", "Email", "Phone", "Unit", "Move-In", "Rent"]
        for c, h in zip(cols, headings):
            self.tree_tenants.heading(c, text=h)
            self.tree_tenants.column(c, anchor="center", width=160)
        self.tree_tenants.column("id", width=70)

        # Scrollbar
        scrollbar = ttk.Scrollbar(self.parent, orient="vertical", command=self.tree_tenants.yview)
        self.tree_tenants.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        
        self.load_tenants()

    def load_tenants(self):
        if not self.tree_tenants:
            return
        for i in self.tree_tenants.get_children():
            self.tree_tenants.delete(i)
        
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute('''
            SELECT t.id, t.full_name, t.email, t.phone, u.unit_number, t.move_in_date, t.monthly_rent
            FROM tenants t LEFT JOIN units u ON t.unit_id = u.id
        ''')
        for row in cur.fetchall():
            unit = row[4] if row[4] else "—"
            rent = f"₱{row[6]:,.2f}" if row[6] else "—"
            self.tree_tenants.insert("", "end", values=(
                row[0], row[1], row[2] or "—", row[3] or "—", unit, row[5], rent
            ))
        conn.close()

    def add_tenant(self):
        AddTenantDialog(self.app, self.load_tenants)

    def delete_tenant(self):
        if not self.tree_tenants:
            return
        sel = self.tree_tenants.selection()
        if not sel:
            return messagebox.showwarning("Select", "Please select a tenant")
        
        tenant_id = self.tree_tenants.item(sel[0])["values"][0]
        if messagebox.askyesno("Delete", "Delete this tenant and all payments?"):
            conn = sqlite3.connect(DB_NAME)
            conn.execute("DELETE FROM tenants WHERE id=?", (tenant_id,))
            conn.commit()
            conn.close()
            self.load_tenants()
