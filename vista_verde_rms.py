#!/usr/bin/env python3
"""
Vista Verde Apartments - RMS
Now connected to database.py
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from apartment_management.database import db   # <-- IMPORT DATABASE MODULE

class VistaVerdeApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Vista Verde Apartments - RMS")
        self.geometry("1400x850")
        self.minsize(1200, 700)
        self.configure(bg="#f0f4f8")

        # User Profile Data
        self.user_data = {
            "first_name": "Ford",
            "last_name": "Asuncion",
            "email": "Ford@gmail.com",
            "phone": "09817225237",
            "location": "Nasugbu, Batangas, Brgy 6 Phugo st.",
            "last_seen": datetime.now().strftime("%B %d, %Y at %I:%M %p")
        }

        self.create_sidebar()
        self.create_main_area()
        self.show_home()

    def create_sidebar(self):
        sidebar = tk.Frame(self, bg="#2c3e50", width=260)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="Vista Verde\nApartments",
                 font=("Helvetica", 18, "bold"), fg="white", bg="#2c3e50",
                 justify="center").pack(pady=60)

        menu_items = [
            ("Home", self.show_home),
            ("Profile", self.show_profile),
            ("Units", self.show_units),
            ("Tenants", lambda: messagebox.showinfo("Info", "Tenants coming soon!")),
            ("Payments", lambda: messagebox.showinfo("Info", "Payments coming soon!")),
            ("Logout", self.destroy)
        ]

        for text, cmd in menu_items:
            btn = tk.Button(sidebar, text=text, font=("Helvetica", 13),
                            bg="#2c3e50", fg="white", bd=0, anchor="w",
                            padx=50, pady=20, command=cmd, cursor="hand2")
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
        canvas = tk.Canvas(self.main_frame, bg="#00a8b5", highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        center = tk.Frame(canvas, bg="#00a8b5")
        center.place(relx=0.5, rely=0.5, anchor="center")

        logo = tk.Canvas(center, width=330, height=330, bg="#00a8b5", highlightthickness=0)
        logo.pack()
        logo.create_oval(40, 40, 290, 290, fill="white", outline="#00d4c0")
        logo.create_polygon(165, 70, 120, 160, 210, 160, fill="#00a8b5")
        logo.create_polygon(165, 100, 100, 200, 230, 200, fill="#00a8b5")

        tk.Label(center, text="VISTAVERDE", font=("Helvetica", 40, "bold"),
                 fg="white", bg="#00a8b5").pack(pady=25)
        tk.Label(center, text="Apartments", font=("Helvetica", 18),
                 fg="#b0f0ff", bg="#00a8b5").pack()

    # ---------------- PROFILE --------------------
    def show_profile(self):
        self.clear_main()
        top = tk.Frame(self.main_frame, bg="#3498db", height=110)
        top.pack(fill="x")
        top.pack_propagate(False)
        tk.Label(top, text=f"Welcome {self.user_data['email']}",
                 font=("Helvetica", 20, "bold"), fg="white",
                 bg="#3498db").pack(side="left", padx=50, pady=35)

        content = tk.Frame(self.main_frame, bg="#f0f4f8")
        content.pack(fill="both", expand=True, padx=60, pady=40)

        left = tk.Frame(content, bg="white", relief="solid", bd=1, width=320)
        left.pack(side="left", padx=(0, 50))
        left.pack_propagate(False)
        photo = tk.Canvas(left, width=220, height=220, bg="white", highlightthickness=0)
        photo.pack(pady=50)
        photo.create_oval(20, 20, 200, 200, fill="#e0e0e0", outline="#aaa", width=4)
        photo.create_text(110, 110, text="FA", font=("Helvetica", 60, "bold"), fill="#888")
        tk.Label(left, text="Ford Asuncion", font=("Helvetica", 16, "bold"), bg="white").pack(pady=10)
        tk.Label(left, text=f"Last Seen: {self.user_data['last_seen']}", fg="gray", bg="white").pack()

    # ---------------- UNITS --------------------
    def show_units(self):
        self.clear_main()

        top = tk.Frame(self.main_frame, bg="#2c3e50")
        top.pack(fill="x", pady=(0, 15))
        tk.Label(top, text="Apartment Units", font=("Helvetica", 20, "bold"),
                 fg="white", bg="#2c3e50").pack(side="left", padx=20, pady=15)

        btn_frame = tk.Frame(top, bg="#2c3e50")
        btn_frame.pack(side="right", padx=20)
        ttk.Button(btn_frame, text="Add Unit", command=self.add_unit).pack(side="right", padx=5)
        ttk.Button(btn_frame, text="Delete Unit", command=self.delete_unit).pack(side="right", padx=5)

        columns = ("id", "unit_number", "unit_type", "monthly_rent", "is_occupied", "created_at")
        self.tree = ttk.Treeview(self.main_frame, columns=columns, show="headings", height=20)
        self.tree.pack(fill="both", expand=True)

        headings = ["Id", "Unit Number", "Unit Type", "Monthly Rent", "Is Occupied", "Created At"]
        for col, text in zip(columns, headings):
            self.tree.heading(col, text=text)
            self.tree.column(col, anchor="center", width=150)

        self.tree.column("id", width=60)
        self.tree.column("is_occupied", width=100)

        scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        self.load_units()

    def load_units(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        units = db.get_all_units()  # <-- LOAD FROM DATABASE MODULE

        for u in units:
            occupied = "Yes" if u["is_occupied"] else "No"
            self.tree.insert("", "end",
                             values=(u["id"], u["unit_number"], u["unit_type"],
                                     f"₱{u['monthly_rent']:,.2f}", occupied, u["created_at"]))

    def add_unit(self):
        dialog = AddUnitDialog(self)
        self.wait_window(dialog)
        self.load_units()

    def delete_unit(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select Unit", "Please select a unit to delete!")
            return

        unit_id = self.tree.item(selected[0])["values"][0]

        if messagebox.askyesno("Confirm Delete", "Delete this unit permanently?"):
            if db.delete_unit(unit_id):   # <-- DELETE USING DATABASE MODULE
                self.load_units()
                messagebox.showinfo("Success", "Unit deleted successfully!")
            else:
                messagebox.showerror("Error", "Delete failed!")

# ---------------- ADD UNIT POPUP --------------------
class AddUnitDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Add New Unit")
        self.geometry("400x500")
        self.configure(bg="#f0f4f8")
        self.resizable(False, False)
        self.grab_set()

        tk.Label(self, text="Add New Apartment Unit", font=("Helvetica", 16, "bold"), bg="#f0f4f8").pack(pady=20)

        form = tk.Frame(self, bg="#f0f4f8")
        form.pack(pady=20, padx=40)

        labels = ["Unit Number (e.g. 101)", "Unit Type (e.g. Studio, 1BR)", "Monthly Rent (₱)"]
        self.entries = {}
        for label in labels:
            tk.Label(form, text=label + ":", bg="#f0f4f8", font=("Helvetica", 11)).pack(anchor="w", pady=8)
            entry = tk.Entry(form, font=("Helvetica", 11), width=30)
            entry.pack(pady=5)
            self.entries[label] = entry

        btn_frame = tk.Frame(self, bg="#f0f4f8")
        btn_frame.pack(pady=30)
        ttk.Button(btn_frame, text="Add Unit", command=self.save_unit).pack(side="left", padx=10)
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side="left", padx=10)

    def save_unit(self):
        unit_num = self.entries["Unit Number (e.g. 101)"].get().strip()
        unit_type = self.entries["Unit Type (e.g. Studio, 1BR)"].get().strip()
        rent_raw = self.entries["Monthly Rent (₱)"].get().strip()

        try:
            rent = float(rent_raw)
        except:
            messagebox.showerror("Invalid", "Monthly rent must be a number!")
            return

        if not unit_num or not unit_type:
            messagebox.showerror("Error", "All fields are required!")
            return

        ok = db.add_unit(unit_num, unit_type, rent)

        if ok:
            messagebox.showinfo("Success", f"Unit {unit_num} added successfully!")
            self.destroy()
        else:
            messagebox.showerror("Error", "Unit number already exists!")

# Run App
if __name__ == "__main__":
    app = VistaVerdeApp()
    app.mainloop()
