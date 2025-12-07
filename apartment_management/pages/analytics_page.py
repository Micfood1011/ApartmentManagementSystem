#!/usr/bin/env python3
"""
Vista Verde Apartments - Analytics Page Module
"""
import tkinter as tk
from tkinter import ttk
import sqlite3
from datetime import datetime

DB_NAME = "vista_verde.db"

class AnalyticsPage:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app

    def show(self):
        # Header
        top = tk.Frame(self.parent, bg="#3498db", height=110)
        top.pack(fill="x")
        top.pack_propagate(False)
        tk.Label(top, text="Payment Analytics & Reports", font=("Helvetica", 20, "bold"),
                 fg="white", bg="#3498db").pack(side="left", padx=50, pady=35)

        # Content area with scrollbar
        content_wrapper = tk.Frame(self.parent, bg="#f0f4f8")
        content_wrapper.pack(fill="both", expand=True)
        
        scroll_canvas = tk.Canvas(content_wrapper, bg="#f0f4f8", highlightthickness=0)
        scrollbar = ttk.Scrollbar(content_wrapper, orient="vertical", command=scroll_canvas.yview)
        scrollable_frame = tk.Frame(scroll_canvas, bg="#f0f4f8")
        
        scrollable_frame.bind("<Configure>",
            lambda e: scroll_canvas.configure(scrollregion=scroll_canvas.bbox("all")))
        
        scroll_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        scroll_canvas.configure(yscrollcommand=scrollbar.set)
        
        scroll_canvas.pack(side="left", fill="both", expand=True, padx=40, pady=30)
        scrollbar.pack(side="right", fill="y")

        self.show_stats_summary(scrollable_frame)
        self.show_monthly_trend(scrollable_frame)
        self.show_recent_payments(scrollable_frame)
        self.show_top_tenants(scrollable_frame)

    def show_stats_summary(self, parent):
        stats_frame = tk.Frame(parent, bg="white", relief="solid", bd=1)
        stats_frame.pack(fill="x", pady=(0, 20))
        
        try:
            conn = sqlite3.connect(DB_NAME)
            cur = conn.cursor()
            
            cur.execute("SELECT COALESCE(SUM(amount), 0) FROM payments")
            total_payments = cur.fetchone()[0]
            electric_bill, water_bill = 15000.00, 8500.00
            cur.execute("SELECT COUNT(*) FROM payments")
            payment_count = cur.fetchone()[0]
            cur.execute("SELECT COALESCE(AVG(amount), 0) FROM payments")
            avg_payment = cur.fetchone()[0]
            cur.execute("SELECT COALESCE(SUM(monthly_rent), 0) FROM units WHERE is_occupied = 1")
            expected_monthly = cur.fetchone()[0]
            conn.close()
            
            tk.Label(stats_frame, text="Payment Summary Dashboard", font=("Helvetica", 16, "bold"),
                    bg="white").pack(pady=15)
            
            # First row
            stats_row1 = tk.Frame(stats_frame, bg="white")
            stats_row1.pack(pady=10, padx=40)
            
            self.create_stat_box(stats_row1, "💰 Total Collected", f"₱{total_payments:,.2f}",
                               "#e8f5e9", "#2e7d32")
            self.create_stat_box(stats_row1, "⚡ Electric Bill", f"₱{electric_bill:,.2f}",
                               "#fff9c4", "#f57f17")
            self.create_stat_box(stats_row1, "📊 Total Payments", str(payment_count),
                               "#fff3e0", "#e65100")
            
            # Second row
            stats_row2 = tk.Frame(stats_frame, bg="white")
            stats_row2.pack(pady=(0, 15), padx=40)
            
            self.create_stat_box(stats_row2, "📈 Average Payment", f"₱{avg_payment:,.2f}",
                               "#f3e5f5", "#6a1b9a")
            self.create_stat_box(stats_row2, "🎯 Expected Monthly", f"₱{expected_monthly:,.2f}",
                               "#fce4ec", "#c2185b")
            self.create_stat_box(stats_row2, "💧 Water Bill", f"₱{water_bill:,.2f}",
                               "#e1f5fe", "#0277bd")
        except sqlite3.Error as e:
            print(f"Error loading stats: {e}")

    def create_stat_box(self, parent, label, value, bg_color, fg_color):
        box = tk.Frame(parent, bg=bg_color, relief="solid", bd=2)
        box.pack(side="left", padx=15, pady=10, ipadx=25, ipady=15)
        tk.Label(box, text=label, font=("Helvetica", 11, "bold"), bg=bg_color).pack()
        tk.Label(box, text=value, font=("Helvetica", 20, "bold"),
                fg=fg_color, bg=bg_color).pack(pady=5)

    def show_monthly_trend(self, parent):
        graph_frame = tk.Frame(parent, bg="white", relief="solid", bd=1)
        graph_frame.pack(fill="x", pady=(0, 20))
        tk.Label(graph_frame, text="Monthly Revenue Trend", font=("Helvetica", 14, "bold"),
                bg="white").pack(pady=15)
        canvas_frame = tk.Frame(graph_frame, bg="white", height=400)
        canvas_frame.pack(fill="both", padx=30, pady=(0, 30))
        canvas_frame.pack_propagate(False)
        self.draw_monthly_trend(canvas_frame)

    def draw_monthly_trend(self, parent):
        graph_canvas = tk.Canvas(parent, bg="white", highlightthickness=0)
        graph_canvas.pack(fill="both", expand=True)
        
        try:
            conn = sqlite3.connect(DB_NAME)
            cur = conn.cursor()
            cur.execute('''SELECT month_covered, SUM(amount) as total FROM payments 
                          WHERE month_covered IS NOT NULL GROUP BY month_covered 
                          ORDER BY month_covered DESC LIMIT 12''')
            monthly_data = list(reversed(cur.fetchall()))
            conn.close()
            
            if not monthly_data:
                graph_canvas.create_text(450, 200, text="No monthly data available",
                                       font=("Helvetica", 14), fill="#999")
                return
            
            width, height = 900, 350
            margin_left, margin_right, margin_top, margin_bottom = 80, 40, 40, 80
            graph_width = width - margin_left - margin_right
            graph_height = height - margin_top - margin_bottom
            max_amount = max(d[1] for d in monthly_data)
            
            # Draw axes
            graph_canvas.create_line(margin_left, height - margin_bottom, width - margin_right,
                                   height - margin_bottom, width=2, fill="#2c3e50")
            graph_canvas.create_line(margin_left, margin_top, margin_left, height - margin_bottom,
                                   width=2, fill="#2c3e50")
            
            # Plot data
            points = []
            for i, (month, amount) in enumerate(monthly_data):
                x = margin_left + (i * graph_width / (len(monthly_data) - 1)) if len(monthly_data) > 1 else margin_left + graph_width / 2
                y = height - margin_bottom - (amount / max_amount * graph_height) if max_amount > 0 else height - margin_bottom
                points.append((x, y))
            
            if len(points) > 1:
                area_points = [(points[0][0], height - margin_bottom)] + points + [(points[-1][0], height - margin_bottom)]
                graph_canvas.create_polygon(area_points, fill="#e3f2fd", outline="")
                for i in range(len(points) - 1):
                    graph_canvas.create_line(points[i][0], points[i][1], points[i+1][0], points[i+1][1],
                                           width=3, fill="#1976d2", smooth=True)
            
            for i, ((month, amount), (x, y)) in enumerate(zip(monthly_data, points)):
                graph_canvas.create_oval(x-6, y-6, x+6, y+6, fill="#1976d2", outline="#0d47a1", width=2)
                graph_canvas.create_text(x, y - 20, text=f"₱{amount:,.0f}",
                                       font=("Helvetica", 9, "bold"), fill="#1976d2")
                month_label = month[5:] if len(month) > 2 else month
                graph_canvas.create_text(x, height - margin_bottom + 20, text=month_label,
                                       font=("Helvetica", 10), fill="#555")
            
            for i in range(6):
                y = height - margin_bottom - (i * graph_height / 5)
                amount = (i * max_amount / 5)
                graph_canvas.create_text(margin_left - 15, y, text=f"₱{amount:,.0f}",
                                       font=("Helvetica", 9), fill="#555", anchor="e")
                graph_canvas.create_line(margin_left - 5, y, margin_left, y, fill="#ccc", width=1)
                graph_canvas.create_line(margin_left, y, width - margin_right, y,
                                       fill="#e0e0e0", width=1, dash=(2, 4))
            
            graph_canvas.create_text(width/2, 15, text="Monthly Revenue Trend (Last 12 Months)",
                                   font=("Helvetica", 12, "bold"), fill="#2c3e50")
        except sqlite3.Error as e:
            graph_canvas.create_text(450, 200, text=f"Error loading data: {e}",
                                   font=("Helvetica", 12), fill="red")

    def show_recent_payments(self, parent):
        table_frame = tk.Frame(parent, bg="white", relief="solid", bd=1)
        table_frame.pack(fill="x", pady=(0, 20))
        tk.Label(table_frame, text="Recent Payments (Last 10)", font=("Helvetica", 14, "bold"),
                bg="white").pack(pady=15)
        
        try:
            conn = sqlite3.connect(DB_NAME)
            cur = conn.cursor()
            cur.execute('''SELECT t.full_name, u.unit_number, p.amount, p.payment_date, p.month_covered
                          FROM payments p JOIN tenants t ON p.tenant_id = t.id 
                          LEFT JOIN units u ON t.unit_id = u.id ORDER BY p.payment_date DESC LIMIT 10''')
            recent = cur.fetchall()
            conn.close()
            
            if recent:
                table = tk.Frame(table_frame, bg="white")
                table.pack(padx=30, pady=(0, 20))
                headers = ["Tenant", "Unit", "Amount", "Date", "Month"]
                for i, header in enumerate(headers):
                    tk.Label(table, text=header, font=("Helvetica", 11, "bold"), bg="#eceff1",
                           width=18, anchor="w", padx=10, pady=8, relief="solid", bd=1).grid(row=0, column=i, sticky="ew")
                for row_idx, (name, unit, amount, date, month) in enumerate(recent, 1):
                    bg_color = "#f5f5f5" if row_idx % 2 == 0 else "white"
                    tk.Label(table, text=name, font=("Helvetica", 10), bg=bg_color, width=18,
                           anchor="w", padx=10, pady=6, relief="solid", bd=1).grid(row=row_idx, column=0, sticky="ew")
                    tk.Label(table, text=unit or "—", font=("Helvetica", 10), bg=bg_color, width=18,
                           anchor="center", padx=10, pady=6, relief="solid", bd=1).grid(row=row_idx, column=1, sticky="ew")
                    tk.Label(table, text=f"₱{amount:,.2f}", font=("Helvetica", 10, "bold"), bg=bg_color,
                           fg="#2e7d32", width=18, anchor="e", padx=10, pady=6, relief="solid", bd=1).grid(row=row_idx, column=2, sticky="ew")
                    tk.Label(table, text=date, font=("Helvetica", 10), bg=bg_color, width=18,
                           anchor="center", padx=10, pady=6, relief="solid", bd=1).grid(row=row_idx, column=3, sticky="ew")
                    tk.Label(table, text=month, font=("Helvetica", 10), bg=bg_color, width=18,
                           anchor="center", padx=10, pady=6, relief="solid", bd=1).grid(row=row_idx, column=4, sticky="ew")
            else:
                tk.Label(table_frame, text="No recent payments", font=("Helvetica", 12),
                        bg="white", fg="#999").pack(pady=20)
        except sqlite3.Error as e:
            tk.Label(table_frame, text=f"Error: {e}", font=("Helvetica", 11),
                    bg="white", fg="red").pack(pady=20)

    def show_top_tenants(self, parent):
        top_frame = tk.Frame(parent, bg="white", relief="solid", bd=1)
        top_frame.pack(fill="x", pady=(0, 20))
        tk.Label(top_frame, text="Top Paying Tenants (Total Contributions)",
                font=("Helvetica", 14, "bold"), bg="white").pack(pady=15)
        
        try:
            conn = sqlite3.connect(DB_NAME)
            cur = conn.cursor()
            cur.execute('''SELECT t.full_name, u.unit_number, COUNT(p.id) as payment_count, SUM(p.amount) as total_paid
                          FROM payments p JOIN tenants t ON p.tenant_id = t.id LEFT JOIN units u ON t.unit_id = u.id
                          GROUP BY t.id ORDER BY total_paid DESC LIMIT 5''')
            top_tenants = cur.fetchall()
            conn.close()
            
            if top_tenants:
                chart_canvas = tk.Canvas(top_frame, bg="white", height=300, highlightthickness=0)
                chart_canvas.pack(fill="x", padx=30, pady=(0, 20))
                max_amount = max(t[3] for t in top_tenants)
                bar_height, spacing, start_y, max_bar_width = 40, 15, 20, 600
                for i, (name, unit, count, total) in enumerate(top_tenants):
                    y = start_y + i * (bar_height + spacing)
                    bar_width = (total / max_amount * max_bar_width) if max_amount > 0 else 0
                    chart_canvas.create_oval(20, y, 50, y + 30, fill="#1976d2", outline="#0d47a1", width=2)
                    chart_canvas.create_text(35, y + 15, text=str(i+1), font=("Helvetica", 14, "bold"), fill="white")
                    chart_canvas.create_text(70, y + 8, text=name, font=("Helvetica", 11, "bold"), anchor="w", fill="#2c3e50")
                    chart_canvas.create_text(70, y + 24, text=f"Unit {unit} • {count} payments",
                                           font=("Helvetica", 9), anchor="w", fill="#666")
                    bar_x = 300
                    chart_canvas.create_rectangle(bar_x, y + 5, bar_x + bar_width, y + bar_height - 5,
                                                 fill="#4caf50", outline="#388e3c", width=2)
                    chart_canvas.create_text(bar_x + bar_width + 10, y + 20, text=f"₱{total:,.2f}",
                                           font=("Helvetica", 11, "bold"), anchor="w", fill="#2e7d32")
                chart_canvas.config(width=900)
            else:
                tk.Label(top_frame, text="No payment data available", font=("Helvetica", 12),
                        bg="white", fg="#999").pack(pady=20)
        except sqlite3.Error as e:
            tk.Label(top_frame, text=f"Error: {e}", font=("Helvetica", 11),
                    bg="white", fg="red").pack(pady=20)