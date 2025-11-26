# database.py
"""
Vista Verde Apartments - Complete Database Module
Handles: Units, Tenants, Payments
Ready for your Tkinter app!
"""
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional, Tuple

DATABASE_NAME = "vista_verde.db"

class VistaVerdeDB:
    def __init__(self, db_name: str = DATABASE_NAME):
        self.db_name = db_name
        self.init_database()

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    def init_database(self):
        """Create all tables if they don't exist"""
        conn = self.get_connection()
        cur = conn.cursor()

        # Units Table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS units (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                unit_number TEXT NOT NULL UNIQUE,
                unit_type TEXT NOT NULL,
                monthly_rent REAL NOT NULL,
                is_occupied INTEGER DEFAULT 0,
                created_at TEXT DEFAULT (datetime('now'))
            )
        ''')

        # Tenants Table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS tenants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                unit_id INTEGER,
                move_in_date TEXT,
                move_out_date TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (unit_id) REFERENCES units (id) ON DELETE SET NULL
            )
        ''')

        # Payments Table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id INTEGER NOT NULL,
                unit_id INTEGER,
                amount_paid REAL NOT NULL,
                payment_date TEXT NOT NULL,
                payment_month TEXT NOT NULL,  -- e.g., "2025-12"
                notes TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (tenant_id) REFERENCES tenants (id) ON DELETE CASCADE,
                FOREIGN KEY (unit_id) REFERENCES units (id)
            )
        ''')

        conn.commit()
        conn.close()

    # ==================== UNITS ====================
    def add_unit(self, unit_number: str, unit_type: str, monthly_rent: float) -> bool:
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO units (unit_number, unit_type, monthly_rent)
                VALUES (?, ?, ?)
            ''', (unit_number, unit_type, monthly_rent))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False  # Unit number already exists

    def get_all_units(self) -> List[Dict]:
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute('''
            SELECT u.*, 
                   t.first_name || ' ' || t.last_name AS tenant_name
            FROM units u
            LEFT JOIN tenants t ON u.id = t.unit_id AND t.is_active = 1
            ORDER BY u.unit_number
        ''')
        rows = cur.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def delete_unit(self, unit_id: int) -> bool:
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM units WHERE id = ?", (unit_id,))
        deleted = cur.rowcount > 0
        conn.commit()
        conn.close()
        return deleted

    # ==================== TENANTS ====================
    def add_tenant(self, first_name: str, last_name: str, email: str, phone: str,
                   unit_id: int, move_in_date: str) -> int:
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO tenants (first_name, last_name, email, phone, unit_id, move_in_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (first_name, last_name, email, phone, unit_id, move_in_date))
        tenant_id = cur.lastrowid
        # Mark unit as occupied
        cur.execute("UPDATE units SET is_occupied = 1 WHERE id = ?", (unit_id,))
        conn.commit()
        conn.close()
        return tenant_id

    def get_all_tenants(self, active_only: bool = True) -> List[Dict]:
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        query = '''
            SELECT t.*, u.unit_number
            FROM tenants t
            LEFT JOIN units u ON t.unit_id = u.id
        '''
        if active_only:
            query += " WHERE t.is_active = 1"
        query += " ORDER BY t.last_name, t.first_name"
        cur.execute(query)
        rows = cur.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def end_tenancy(self, tenant_id: int, move_out_date: str):
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute('''
            UPDATE tenants 
            SET is_active = 0, move_out_date = ?
            WHERE id = ?
        ''', (move_out_date, tenant_id))
        # Free the unit
        cur.execute('''
            UPDATE units 
            SET is_occupied = 0 
            WHERE id = (SELECT unit_id FROM tenants WHERE id = ?)
        ''', (tenant_id,))
        conn.commit()
        conn.close()

    # ==================== PAYMENTS ====================
    def add_payment(self, tenant_id: int, amount_paid: float,
                    payment_month: str, notes: str = "") -> bool:
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO payments (tenant_id, unit_id, amount_paid, payment_date, payment_month, notes)
            VALUES (?, 
                    (SELECT unit_id FROM tenants WHERE id = ?),
                    ?, date('now'), ?, ?)
        ''', (tenant_id, tenant_id, amount_paid, payment_month, notes))
        conn.commit()
        conn.close()
        return True

    def get_payments_by_month(self, year_month: str) -> List[Dict]:
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute('''
            SELECT p.*, t.first_name || ' ' || t.last_name AS tenant_name, u.unit_number
            FROM payments p
            JOIN tenants t ON p.tenant_id = t.id
            JOIN units u ON p.unit_id = u.id
            WHERE p.payment_month = ?
            ORDER BY p.payment_date DESC
        ''', (year_month,))
        rows = cur.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_tenant_payment_status(self, tenant_id: int) -> List[Dict]:
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute('''
            SELECT payment_month, amount_paid, payment_date
            FROM payments
            WHERE tenant_id = ?
            ORDER BY payment_month DESC
        ''', (tenant_id,))
        rows = cur.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    # ==================== UTILITIES ====================
    def get_summary(self) -> Dict:
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM units")
        total_units = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM units WHERE is_occupied = 1")
        occupied = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM tenants WHERE is_active = 1")
        active_tenants = cur.fetchone()[0]
        cur.execute("SELECT COALESCE(SUM(amount_paid), 0) FROM payments WHERE strftime('%Y-%m', payment_date) = strftime('%Y-%m', 'now')")
        monthly_income = cur.fetchone()[0]
        conn.close()

        return {
            "total_units": total_units,
            "occupied_units": occupied,
            "vacant_units": total_units - occupied,
            "active_tenants": active_tenants,
            "monthly_income": monthly_income
        }

# Create instance for easy import


# Auto-create database on import
if __name__ == "__main__":
    print("Vista Verde Database Created Successfully!")
    print(VistaVerdeDB.get_summary())