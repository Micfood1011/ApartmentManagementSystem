#!/usr/bin/env python3
"""
Vista Verde Apartments - Login Page
"""
import tkinter as tk
from tkinter import messagebox

class LoginPage(tk.Tk):
    def __init__(self, on_success):
        super().__init__()
        self.title("Vista Verde Apartments - Login")
        self.configure(bg="#00a8b5")
        self.on_success = on_success
        
        # Make fullscreen
        self.attributes('-fullscreen', True)
        
        # Bind Escape key to exit fullscreen (optional)
        self.bind('<Escape>', lambda e: self.attributes('-fullscreen', False))
        
        # Create login UI
        self.create_login_ui()
    
    def create_login_ui(self):
        # Main container
        main_frame = tk.Frame(self, bg="#00a8b5")
        main_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Logo
        logo_canvas = tk.Canvas(main_frame, width=200, height=200, 
                               bg="#00a8b5", highlightthickness=0)
        logo_canvas.pack(pady=(0, 20))
        
        # Draw logo circles and triangles
        logo_canvas.create_oval(30, 30, 170, 170, fill="white", outline="#00d4c0", width=3)
        logo_canvas.create_polygon(100, 50, 70, 110, 130, 110, fill="#00a8b5")
        logo_canvas.create_polygon(100, 75, 55, 135, 145, 135, fill="#00a8b5")
        
        # Title
        tk.Label(main_frame, text="VISTAVERDE", font=("Helvetica", 32, "bold"),
                fg="white", bg="#00a8b5").pack(pady=(0, 5))
        tk.Label(main_frame, text="Apartments", font=("Helvetica", 16),
                fg="#b0f8ff", bg="#00a8b5").pack(pady=(0, 30))
        
        # Login form container with white background
        form_frame = tk.Frame(main_frame, bg="white", relief="solid", bd=2)
        form_frame.pack(pady=20, padx=40, ipadx=40, ipady=30)
        
        # Login header
        tk.Label(form_frame, text="LOGIN", font=("Helvetica", 18, "bold"),
                fg="#2c3e50", bg="white").pack(pady=(10, 20))
        
        # Username field
        tk.Label(form_frame, text="Username", font=("Helvetica", 11),
                fg="#34495e", bg="white", anchor="w").pack(anchor="w", padx=20, pady=(10, 5))
        
        self.username_entry = tk.Entry(form_frame, width=30, font=("Helvetica", 12),
                                       relief="solid", bd=1)
        self.username_entry.pack(padx=20, pady=(0, 15), ipady=8)
        self.username_entry.focus()
        
        # Password field
        tk.Label(form_frame, text="Password", font=("Helvetica", 11),
                fg="#34495e", bg="white", anchor="w").pack(anchor="w", padx=20, pady=(5, 5))
        
        self.password_entry = tk.Entry(form_frame, width=30, font=("Helvetica", 12),
                                       show="●", relief="solid", bd=1)
        self.password_entry.pack(padx=20, pady=(0, 20), ipady=8)
        
        # Bind Enter key to login
        self.username_entry.bind("<Return>", lambda e: self.password_entry.focus())
        self.password_entry.bind("<Return>", lambda e: self.login())
        
        # Login button
        login_btn = tk.Button(form_frame, text="LOGIN", font=("Helvetica", 12, "bold"),
                            bg="#00a8b5", fg="white", width=25, height=2,
                            relief="flat", cursor="hand2", command=self.login)
        login_btn.pack(pady=(10, 15))
        
        # Hover effects
        login_btn.bind("<Enter>", lambda e: login_btn.config(bg="#008c96"))
        login_btn.bind("<Leave>", lambda e: login_btn.config(bg="#00a8b5"))
        
        # Footer text
        tk.Label(main_frame, text="Rental Management System",
                font=("Helvetica", 10), fg="#b0f8ff", bg="#00a8b5").pack(pady=(20, 0))
        tk.Label(main_frame, text="© 2025 Vista Verde Apartments",
                font=("Helvetica", 9), fg="#80d8e0", bg="#00a8b5").pack(pady=(5, 0))
    
    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        # Check credentials
        if username == "admin" and password == "Admin123":
            self.destroy()
            self.on_success()
        else:
            messagebox.showerror("Login Failed", 
                               "Invalid username or password!\n\nPlease try again.")
            self.password_entry.delete(0, tk.END)
            self.username_entry.focus()

# This function is what gets imported
def show_login(on_success):
    """Show login page"""
    app = LoginPage(on_success)
    app.mainloop()

# For testing the login page standalone
if __name__ == "__main__":
    def test_success():
        print("Login successful!")
    show_login(test_success)
