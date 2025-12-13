#!/usr/bin/env python3
"""
Vista Verde Apartments - Add Unit Dialog
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import sqlite3

DB_NAME = "vista_verde.db"

class AddUnitDialog(tk.Toplevel):
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.title("Add Unit")
        self.geometry("400x400")
        self.resizable(False, False)
        self.grab_set()
        self.callback = callback
        
        # Title
        tk.Label(self, text="Add New Unit", font=("Helvetica", 16, "bold")).pack(pady=20)
        
        # Form fields
        fields = ["Unit Number (e.g. 101)", "Unit Type", "Monthly Rent (₱)"]
        self.entries = {}
        
        for f in fields:
            tk.Label(self, text=f + ":").pack(anchor="w", padx=50, pady=8)
            e = tk.Entry(self, width=30)
            e.pack(pady=5, padx=50)
            self.entries[f] = e
        
        # Buttons
        btns = tk.Frame(self)
        btns.pack(pady=30)
        ttk.Button(btns, text="Add", command=self.save).pack(side="left", padx=10)
        ttk.Button(btns, text="Cancel", command=self.destroy).pack(side="left", padx=10)

    def save(self):
        num = self.entries["Unit Number (e.g. 101)"].get().strip()
        typ = self.entries["Unit Type"].get().strip()
        
        try:
            rent = float(self.entries["Monthly Rent (₱)"].get())
        except:
            return messagebox.showerror("Error", "Rent must be a number")
        
        if not num or not typ:
            return messagebox.showerror("Error", "All fields required")
        
        conn = sqlite3.connect(DB_NAME)
        try:
            conn.execute(
                "INSERT INTO units (unit_number, unit_type, monthly_rent, created_at) VALUES (?, ?, ?, ?)",
                (num, typ, rent, datetime.now().strftime("%Y-%m-%d"))
            )
            conn.commit()
            messagebox.showinfo("Success", f"Unit {num} added!")
            self.callback()
            self.destroy()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Unit number already exists")
        finally:
            conn.close()
