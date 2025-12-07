#!/usr/bin/env python3
"""
Vista Verde Apartments - Home Page Module
"""
import tkinter as tk
import sqlite3

DB_NAME = "vista_verde.db"

class HomePage:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app

    def show(self):
        canvas = tk.Canvas(self.parent, bg="#00a8b5", highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        center = tk.Frame(canvas, bg="#00a8b5")
        center.place(relx=0.5, rely=0.5, anchor="center")

        # Logo
        logo = tk.Canvas(center, width=340, height=340, bg="#00a8b5", highlightthickness=0)
        logo.pack()
        logo.create_oval(40, 40, 300, 300, fill="white", outline="#00d4c0")
        logo.create_polygon(170, 70, 120, 170, 220, 170, fill="#00a8b5")
        logo.create_polygon(170, 110, 100, 220, 240, 220, fill="#00a8b5")

        tk.Label(center, text="VISTAVERDE", font=("Helvetica", 42, "bold"),
                 fg="white", bg="#00a8b5").pack(pady=30)
        tk.Label(center, text="Apartments", font=("Helvetica", 20),
                 fg="#b0f8ff", bg="#00a8b5").pack()
        
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