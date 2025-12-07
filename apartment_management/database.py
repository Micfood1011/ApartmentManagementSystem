#!/usr/bin/env python3
"""
Vista Verde Apartments - Database Creation Script
Filename: database.py
This script creates and initializes the SQLite database with sample data
Owner: Ford Asuncion

Usage:
    python database.py          # Create database with sample data
    python vista_verde.py       # Run the main application after setup
"""

import sqlite3
from datetime import datetime

DB_NAME = "vista_verde.db"

def create_database():
    """Create the database and all tables"""
    print("🏢 Vista Verde Apartments - Database Setup")
    print("=" * 50)
    
    try:
        # Connect to database (creates file if doesn't exist)
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        
        print("\n📊 Creating tables...")
        
        # ==================== UNITS TABLE ====================
        cur.execute('''
            CREATE TABLE IF NOT EXISTS units (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                unit_number TEXT UNIQUE NOT NULL,
                unit_type TEXT,
                monthly_rent REAL,
                is_occupied INTEGER DEFAULT 0,
                created_at TEXT,
                CONSTRAINT chk_occupied CHECK (is_occupied IN (0, 1))
            )
        ''')
        print("   ✓ Units table created")
        
        # Create indexes for units
        cur.execute('CREATE INDEX IF NOT EXISTS idx_units_number ON units(unit_number)')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_units_occupied ON units(is_occupied)')
        
        # ==================== TENANTS TABLE ====================
        cur.execute('''
            CREATE TABLE IF NOT EXISTS tenants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                unit_id INTEGER,
                move_in_date TEXT,
                monthly_rent REAL,
                FOREIGN KEY (unit_id) REFERENCES units(id) ON DELETE SET NULL
            )
        ''')
        print("   ✓ Tenants table created")
        
        # Create indexes for tenants
        cur.execute('CREATE INDEX IF NOT EXISTS idx_tenants_name ON tenants(full_name)')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_tenants_unit ON tenants(unit_id)')
        
        # ==================== PAYMENTS TABLE ====================
        cur.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                payment_date TEXT NOT NULL,
                month_covered TEXT,
                FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE
            )
        ''')
        print("   ✓ Payments table created")
        
        # Create indexes for payments
        cur.execute('CREATE INDEX IF NOT EXISTS idx_payments_tenant ON payments(tenant_id)')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_payments_date ON payments(payment_date)')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_payments_month ON payments(month_covered)')
        
        # ==================== UTILITY BILLS TABLE ====================
        cur.execute('''
            CREATE TABLE IF NOT EXISTS utility_bills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bill_type TEXT NOT NULL,
                amount REAL NOT NULL,
                billing_month TEXT NOT NULL,
                due_date TEXT,
                paid INTEGER DEFAULT 0,
                created_at TEXT,
                CONSTRAINT chk_bill_type CHECK (bill_type IN ('electric', 'water', 'gas', 'internet'))
            )
        ''')
        print("   ✓ Utility bills table created")
        
        # Create indexes for utility bills
        cur.execute('CREATE INDEX IF NOT EXISTS idx_bills_type ON utility_bills(bill_type)')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_bills_month ON utility_bills(billing_month)')
        
        # ==================== TRIGGERS ====================
        print("\n🔄 Creating triggers...")
        
        # Trigger to update unit occupancy when tenant is added
        cur.execute('''
            CREATE TRIGGER IF NOT EXISTS update_unit_occupancy_on_tenant_insert
            AFTER INSERT ON tenants
            WHEN NEW.unit_id IS NOT NULL
            BEGIN
                UPDATE units SET is_occupied = 1 WHERE id = NEW.unit_id;
            END
        ''')
        print("   ✓ Tenant insert trigger created")
        
        # Trigger to free up unit when tenant is deleted
        cur.execute('''
            CREATE TRIGGER IF NOT EXISTS update_unit_occupancy_on_tenant_delete
            AFTER DELETE ON tenants
            WHEN OLD.unit_id IS NOT NULL
            BEGIN
                UPDATE units SET is_occupied = 0 WHERE id = OLD.unit_id;
            END
        ''')
        print("   ✓ Tenant delete trigger created")
        
        # Trigger to handle unit change
        cur.execute('''
            CREATE TRIGGER IF NOT EXISTS update_unit_occupancy_on_tenant_update
            AFTER UPDATE OF unit_id ON tenants
            BEGIN
                UPDATE units SET is_occupied = 0 WHERE id = OLD.unit_id AND OLD.unit_id IS NOT NULL;
                UPDATE units SET is_occupied = 1 WHERE id = NEW.unit_id AND NEW.unit_id IS NOT NULL;
            END
        ''')
        print("   ✓ Tenant update trigger created")
        
        conn.commit()
        print("\n✅ Database structure created successfully!")
        
        return conn, cur
        
    except sqlite3.Error as e:
        print(f"\n❌ Error creating database: {e}")
        return None, None


def insert_sample_data(conn, cur):
    """Insert sample data for testing - ENHANCED VERSION"""
    print("\n📝 Inserting sample data...")
    
    try:
        # Check if data already exists
        cur.execute("SELECT COUNT(*) FROM units")
        if cur.fetchone()[0] > 0:
            print("   ⚠️  Sample data already exists. Skipping...")
            return
        
        # Insert sample units
        units_data = [
            ('101', 'Studio', 8000.00, 1, '2024-01-15'),
            ('102', '1 Bedroom', 12000.00, 1, '2024-01-15'),
            ('103', '2 Bedroom', 18000.00, 1, '2024-01-15'),
            ('201', 'Studio', 8500.00, 1, '2024-02-01'),
            ('202', '1 Bedroom', 12500.00, 1, '2024-02-01'),
            ('203', '2 Bedroom', 19000.00, 0, '2024-02-01'),
            ('301', 'Studio', 9000.00, 0, '2024-03-10'),
            ('302', '1 Bedroom', 13000.00, 0, '2024-03-10'),
        ]
        
        cur.executemany(
            'INSERT INTO units (unit_number, unit_type, monthly_rent, is_occupied, created_at) VALUES (?, ?, ?, ?, ?)',
            units_data
        )
        print(f"   ✓ Added {len(units_data)} units")
        
        # Insert sample tenants - ENHANCED
        tenants_data = [
            ('Maria Santos', 'maria.santos@email.com', '09171234567', 1, '2024-01-15', 8000.00),
            ('Juan Dela Cruz', 'juan.delacruz@email.com', '09281234567', 2, '2024-01-20', 12000.00),
            ('Ana Reyes', 'ana.reyes@email.com', '09391234567', 4, '2024-02-01', 8500.00),
            ('Carlos Mendoza', 'carlos.m@email.com', '09451234567', 3, '2024-02-10', 18000.00),
            ('Sofia Garcia', 'sofia.garcia@email.com', '09561234567', 5, '2024-03-01', 12500.00),
        ]
        
        cur.executemany(
            'INSERT INTO tenants (full_name, email, phone, unit_id, move_in_date, monthly_rent) VALUES (?, ?, ?, ?, ?, ?)',
            tenants_data
        )
        print(f"   ✓ Added {len(tenants_data)} tenants")
        
        # Insert sample payments - MUCH MORE DATA FOR BETTER ANALYTICS
        payments_data = [
            # Maria Santos (Tenant 1) - Unit 101 - ₱8,000/month
            (1, 8000.00, '2024-02-01', '2024-02'),
            (1, 8000.00, '2024-03-01', '2024-03'),
            (1, 8000.00, '2024-04-01', '2024-04'),
            (1, 8000.00, '2024-05-01', '2024-05'),
            (1, 8000.00, '2024-06-01', '2024-06'),
            (1, 8000.00, '2024-07-01', '2024-07'),
            (1, 8000.00, '2024-08-01', '2024-08'),
            (1, 8000.00, '2024-09-01', '2024-09'),
            (1, 8000.00, '2024-10-01', '2024-10'),
            (1, 8000.00, '2024-11-01', '2024-11'),
            (1, 8000.00, '2024-12-01', '2024-12'),
            
            # Juan Dela Cruz (Tenant 2) - Unit 102 - ₱12,000/month
            (2, 12000.00, '2024-02-01', '2024-02'),
            (2, 12000.00, '2024-03-01', '2024-03'),
            (2, 12000.00, '2024-04-01', '2024-04'),
            (2, 12000.00, '2024-05-01', '2024-05'),
            (2, 12000.00, '2024-06-01', '2024-06'),
            (2, 12000.00, '2024-07-01', '2024-07'),
            (2, 12000.00, '2024-08-01', '2024-08'),
            (2, 12000.00, '2024-09-01', '2024-09'),
            (2, 12000.00, '2024-10-01', '2024-10'),
            (2, 12000.00, '2024-11-01', '2024-11'),
            (2, 12000.00, '2024-12-01', '2024-12'),
            
            # Ana Reyes (Tenant 3) - Unit 201 - ₱8,500/month
            (3, 8500.00, '2024-02-15', '2024-02'),
            (3, 8500.00, '2024-03-15', '2024-03'),
            (3, 8500.00, '2024-04-15', '2024-04'),
            (3, 8500.00, '2024-05-15', '2024-05'),
            (3, 8500.00, '2024-06-15', '2024-06'),
            (3, 8500.00, '2024-07-15', '2024-07'),
            (3, 8500.00, '2024-08-15', '2024-08'),
            (3, 8500.00, '2024-09-15', '2024-09'),
            (3, 8500.00, '2024-10-15', '2024-10'),
            (3, 8500.00, '2024-11-15', '2024-11'),
            (3, 8500.00, '2024-12-05', '2024-12'),
            
            # Carlos Mendoza (Tenant 4) - Unit 103 - ₱18,000/month
            (4, 18000.00, '2024-03-01', '2024-03'),
            (4, 18000.00, '2024-04-01', '2024-04'),
            (4, 18000.00, '2024-05-01', '2024-05'),
            (4, 18000.00, '2024-06-01', '2024-06'),
            (4, 18000.00, '2024-07-01', '2024-07'),
            (4, 18000.00, '2024-08-01', '2024-08'),
            (4, 18000.00, '2024-09-01', '2024-09'),
            (4, 18000.00, '2024-10-01', '2024-10'),
            (4, 18000.00, '2024-11-01', '2024-11'),
            (4, 18000.00, '2024-12-02', '2024-12'),
            
            # Sofia Garcia (Tenant 5) - Unit 202 - ₱12,500/month
            (5, 12500.00, '2024-03-05', '2024-03'),
            (5, 12500.00, '2024-04-05', '2024-04'),
            (5, 12500.00, '2024-05-05', '2024-05'),
            (5, 12500.00, '2024-06-05', '2024-06'),
            (5, 12500.00, '2024-07-05', '2024-07'),
            (5, 12500.00, '2024-08-05', '2024-08'),
            (5, 12500.00, '2024-09-05', '2024-09'),
            (5, 12500.00, '2024-10-05', '2024-10'),
            (5, 12500.00, '2024-11-05', '2024-11'),
            (5, 12500.00, '2024-12-03', '2024-12'),
        ]
        
        cur.executemany(
            'INSERT INTO payments (tenant_id, amount, payment_date, month_covered) VALUES (?, ?, ?, ?)',
            payments_data
        )
        print(f"   ✓ Added {len(payments_data)} payment records")
        
        # Insert sample utility bills
        utility_bills_data = [
            # Electric bills
            ('electric', 15000.00, '2024-01', '2024-01-20', 1, '2024-01-05'),
            ('electric', 14500.00, '2024-02', '2024-02-20', 1, '2024-02-05'),
            ('electric', 16200.00, '2024-03', '2024-03-20', 1, '2024-03-05'),
            ('electric', 15800.00, '2024-04', '2024-04-20', 1, '2024-04-05'),
            ('electric', 17000.00, '2024-05', '2024-05-20', 1, '2024-05-05'),
            ('electric', 16500.00, '2024-06', '2024-06-20', 1, '2024-06-05'),
            ('electric', 17500.00, '2024-07', '2024-07-20', 1, '2024-07-05'),
            ('electric', 16800.00, '2024-08', '2024-08-20', 1, '2024-08-05'),
            ('electric', 15900.00, '2024-09', '2024-09-20', 1, '2024-09-05'),
            ('electric', 16300.00, '2024-10', '2024-10-20', 1, '2024-10-05'),
            ('electric', 17200.00, '2024-11', '2024-11-20', 1, '2024-11-05'),
            ('electric', 15000.00, '2024-12', '2024-12-20', 0, '2024-12-05'),
            
            # Water bills
            ('water', 8500.00, '2024-01', '2024-01-15', 1, '2024-01-05'),
            ('water', 8200.00, '2024-02', '2024-02-15', 1, '2024-02-05'),
            ('water', 8800.00, '2024-03', '2024-03-15', 1, '2024-03-05'),
            ('water', 8600.00, '2024-04', '2024-04-15', 1, '2024-04-05'),
            ('water', 9000.00, '2024-05', '2024-05-15', 1, '2024-05-05'),
            ('water', 8700.00, '2024-06', '2024-06-15', 1, '2024-06-05'),
            ('water', 9200.00, '2024-07', '2024-07-15', 1, '2024-07-05'),
            ('water', 8900.00, '2024-08', '2024-08-15', 1, '2024-08-05'),
            ('water', 8400.00, '2024-09', '2024-09-15', 1, '2024-09-05'),
            ('water', 8600.00, '2024-10', '2024-10-15', 1, '2024-10-05'),
            ('water', 9100.00, '2024-11', '2024-11-15', 1, '2024-11-05'),
            ('water', 8500.00, '2024-12', '2024-12-15', 0, '2024-12-05'),
        ]
        
        cur.executemany(
            'INSERT INTO utility_bills (bill_type, amount, billing_month, due_date, paid, created_at) VALUES (?, ?, ?, ?, ?, ?)',
            utility_bills_data
        )
        print(f"   ✓ Added {len(utility_bills_data)} utility bill records")
        
        conn.commit()
        print("\n✅ Sample data inserted successfully!")
        
    except sqlite3.Error as e:
        print(f"\n❌ Error inserting sample data: {e}")
        conn.rollback()


def display_summary(cur):
    """Display database summary"""
    print("\n" + "=" * 50)
    print("📊 DATABASE SUMMARY")
    print("=" * 50)
    
    try:
        # Count units
        cur.execute("SELECT COUNT(*), SUM(is_occupied) FROM units")
        total_units, occupied = cur.fetchone()
        available = total_units - (occupied or 0)
        print(f"\n🏢 Units:")
        print(f"   Total: {total_units}")
        print(f"   Occupied: {occupied or 0}")
        print(f"   Available: {available}")
        
        # Count tenants
        cur.execute("SELECT COUNT(*) FROM tenants")
        total_tenants = cur.fetchone()[0]
        print(f"\n👥 Tenants: {total_tenants}")
        
        # Count payments and total revenue
        cur.execute("SELECT COUNT(*), SUM(amount) FROM payments")
        total_payments, total_revenue = cur.fetchone()
        print(f"\n💰 Payments:")
        print(f"   Total Transactions: {total_payments}")
        print(f"   Total Revenue: ₱{total_revenue:,.2f}" if total_revenue else "   Total Revenue: ₱0.00")
        
        # Count utility bills
        cur.execute("SELECT COUNT(*), SUM(amount) FROM utility_bills")
        total_bills, total_bills_amount = cur.fetchone()
        print(f"\n⚡ Utility Bills:")
        print(f"   Total Bills: {total_bills}")
        print(f"   Total Amount: ₱{total_bills_amount:,.2f}" if total_bills_amount else "   Total Amount: ₱0.00")
        
        # Recent payments
        cur.execute('''
            SELECT t.full_name, p.amount, p.payment_date
            FROM payments p
            JOIN tenants t ON p.tenant_id = t.id
            ORDER BY p.payment_date DESC
            LIMIT 5
        ''')
        recent = cur.fetchall()
        if recent:
            print(f"\n📅 Recent Payments:")
            for name, amount, date in recent:
                print(f"   • {name}: ₱{amount:,.2f} on {date}")
        
        print("\n" + "=" * 50)
        print("✅ Database is ready to use!")
        print(f"📁 Database file: {DB_NAME}")
        print("🚀 Run your main application: python vista_verde_rms.py")
        print("=" * 50)
        
    except sqlite3.Error as e:
        print(f"\n❌ Error displaying summary: {e}")


def main():
    """Main function to create database"""
    print("\n🚀 Starting Vista Verde database setup...\n")
    
    # Create database and tables
    conn, cur = create_database()
    
    if conn and cur:
        # Insert sample data
        insert_sample_data(conn, cur)
        
        # Display summary
        display_summary(cur)
        
        # Close connection
        conn.close()
        print("\n✅ Database connection closed.")
        print("\n✨ Setup complete! Your database is ready.\n")
    else:
        print("\n❌ Database setup failed.")


if __name__ == "__main__":
    main()
