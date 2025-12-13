#!/usr/bin/env python3
"""
Vista Verde Apartments - Add Tenant Dialog
"""
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

DB_NAME = "vista_verde.db"

class AddTenantDialog(tk.Toplevel):
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.title("Add Tenant")
        self.geometry("500x650")
        self.grab_set()
        self.callback = callback
        
        # Title
        tk.Label(self, text="Add New Tenant", font=("Helvetica", 16, "bold")).pack(pady=20)

        # Form fields
        self.entries = {}
        labels = ["Full Name", "Email", "Phone", "Move-In Date (YYYY-MM-DD)"]
        
        for l in labels:
            tk.Label(self, text=l + ":").pack(anchor="w", padx=60, pady=8)
            e = tk.Entry(self, width=40)
            e.pack(pady=5)
            self.entries[l] = e

        # Unit selection
        tk.Label(self, text="Assign to Unit:").pack(anchor="w", padx=60, pady=(20,5))
        self.unit_var = tk.StringVar()
        combo = ttk.Combobox(self, textvariable=self.unit_var, state="readonly", width=37)
        combo.pack(pady=5, padx=60)
        
        # Unit type display label (initially hidden)
        self.unit_type_label = tk.Label(
            self, 
            text="", 
            font=("Helvetica", 11, "italic"),
            fg="#2980b9"
        )
        self.unit_type_label.pack(pady=(5, 0), padx=60)
        
        # Load available units with their types
        conn = sqlite3.connect(DB_NAME)
        units = conn.execute(
            "SELECT id, unit_number, unit_type, monthly_rent FROM units WHERE is_occupied = 0"
        ).fetchall()
        combo['values'] = [f"{u[1]} (Available)" for u in units]
        
        # Store unit data including type and rent
        self.unit_data = {
            f"{u[1]} (Available)": {
                'id': u[0],
                'type': u[2],
                'rent': u[3]
            } 
            for u in units
        }
        conn.close()
        
        # Bind selection event to show unit type
        combo.bind("<<ComboboxSelected>>", self.on_unit_selected)

        # Buttons
        btns = tk.Frame(self)
        btns.pack(pady=30)
        ttk.Button(btns, text="Add Tenant", command=self.save).pack(side="left", padx=10)
        ttk.Button(btns, text="Cancel", command=self.destroy).pack(side="left", padx=10)

    def on_unit_selected(self, event=None):
        """Display unit type and rent when a unit is selected"""
        unit_text = self.unit_var.get()
        if unit_text and unit_text in self.unit_data:
            unit_info = self.unit_data[unit_text]
            unit_type = unit_info['type'] or "Standard"
            rent = unit_info['rent']
            
            # Display unit type and rent
            self.unit_type_label.config(
                text=f"Unit Type: {unit_type} • Monthly Rent: ₱{rent:,.2f}"
            )
        else:
            self.unit_type_label.config(text="")

    def save(self):
        name = self.entries["Full Name"].get().strip()
        email = self.entries["Email"].get().strip()
        phone = self.entries["Phone"].get().strip()
        date_in = self.entries["Move-In Date (YYYY-MM-DD)"].get().strip()
        unit_text = self.unit_var.get()
        
        if not name or not date_in:
            return messagebox.showerror("Error", "Name and Move-In Date required")

        if not unit_text:
            return messagebox.showerror("Error", "Please select a unit")
        
        unit_info = self.unit_data.get(unit_text)
        if not unit_info:
            return messagebox.showerror("Error", "Invalid unit selection")
        
        unit_id = unit_info['id']
        rent = unit_info['rent']
        
        conn = sqlite3.connect(DB_NAME)
        
        try:
            conn.execute(
                "INSERT INTO tenants (full_name, email, phone, unit_id, move_in_date, monthly_rent) VALUES (?, ?, ?, ?, ?, ?)",
                (name, email or None, phone or None, unit_id, date_in, rent)
            )
            
            # Mark unit as occupied
            conn.execute("UPDATE units SET is_occupied = 1 WHERE id=?", (unit_id,))
            
            conn.commit()
            messagebox.showinfo("Success", f"Tenant {name} added successfully!")
            self.callback()
            self.destroy()
            
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Error", f"Failed to add tenant: {str(e)}")
        finally:
            conn.close()
