#!/usr/bin/env python3
"""Vista Verde Apartments - Units Page Module"""
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from dialogs.add_unit_dialog import AddUnitDialog

DB_NAME = "vista_verde.db"

class UnitsPage:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.tree_units = None

    def show(self):
        top = tk.Frame(self.parent, bg="#2c3e50")
        top.pack(fill="x", pady=(0,15))
        tk.Label(top, text="Apartment Units", font=("Helvetica", 20, "bold"),
                fg="white", bg="#2c3e50").pack(side="left", padx=20, pady=15)
        btns = tk.Frame(top, bg="#2c3e50")
        btns.pack(side="right", padx=20)
        ttk.Button(btns, text="Add Unit", command=self.add_unit).pack(side="right", padx=5)
        ttk.Button(btns, text="Delete Unit", command=self.delete_unit).pack(side="right", padx=5)

        columns = ("id", "unit_number", "unit_type", "rent", "occupied", "created")
        self.tree_units = ttk.Treeview(self.parent, columns=columns, show="headings")
        self.tree_units.pack(fill="both", expand=True)
        for col, text in zip(columns, ["ID", "Unit Number", "Type", "Monthly Rent", "Occupied", "Created"]):
            self.tree_units.heading(col, text=text)
            self.tree_units.column(col, anchor="center", width=150)
        self.tree_units.column("id", width=70)

        scrollbar = ttk.Scrollbar(self.parent, orient="vertical", command=self.tree_units.yview)
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
            self.tree_units.insert("", "end", values=(row[0], row[1], row[2],
                                   f"₱{row[3]:,.2f}", occupied, row[5]))
        conn.close()

    def add_unit(self):
        AddUnitDialog(self.app, self.load_units)

    def delete_unit(self):
        sel = self.tree_units.selection()
        if not sel: return messagebox.showwarning("Select", "Please select a unit")
        unit_id = self.tree_units.item(sel[0])["values"][0]
        if messagebox.askyesno("Delete", "Delete this unit?"):
            conn = sqlite3.connect(DB_NAME)
            conn.execute("DELETE FROM units WHERE id=?", (unit_id,))
            conn.commit(); conn.close()
            self.load_units()