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
    """Insert sample data for testing"""
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
            ('103', '2 Bedroom', 18000.00, 0, '2024-01-15'),
            ('201', 'Studio', 8500.00, 1, '2024-02-01'),
            ('202', '1 Bedroom', 12500.00, 0, '2024-02-01'),
            ('203', '2 Bedroom', 19000.00, 0, '2024-02-01'),
            ('301', 'Studio', 9000.00, 0, '2024-03-10'),
            ('302', '1 Bedroom', 13000.00, 0, '2024-03-10'),
        ]
        
        cur.executemany(
            'INSERT INTO units (unit_number, unit_type, monthly_rent, is_occupied, created_at) VALUES (?, ?, ?, ?, ?)',
            units_data
        )
        print(f"   ✓ Added {len(units_data)} units")
        
        # Insert sample tenants
        tenants_data = [
            ('Maria Santos', 'maria.santos@email.com', '09171234567', 1, '2024-02-01', 8000.00),
            ('Juan Dela Cruz', 'juan.delacruz@email.com', '09281234567', 2, '2024-02-15', 12000.00),
            ('Ana Reyes', 'ana.reyes@email.com', '09391234567', 4, '2024-03-01', 8500.00),
        ]
        
        cur.executemany(
            'INSERT INTO tenants (full_name, email, phone, unit_id, move_in_date, monthly_rent) VALUES (?, ?, ?, ?, ?, ?)',
            tenants_data
        )
        print(f"   ✓ Added {len(tenants_data)} tenants")
        
        # Insert sample payments
        payments_data = [
            (1, 8000.00, '2024-02-01', '2024-02'),
            (1, 8000.00, '2024-03-01', '2024-03'),
            (1, 8000.00, '2024-04-01', '2024-04'),
            (1, 8000.00, '2024-11-01', '2024-11'),
            (2, 12000.00, '2024-03-01', '2024-03'),
            (2, 12000.00, '2024-04-01', '2024-04'),
            (2, 12000.00, '2024-11-01', '2024-11'),
            (3, 8500.00, '2024-03-15', '2024-03'),
            (3, 8500.00, '2024-04-15', '2024-04'),
            (3, 8500.00, '2024-11-15', '2024-11'),
        ]
        
        cur.executemany(
            'INSERT INTO payments (tenant_id, amount, payment_date, month_covered) VALUES (?, ?, ?, ?)',
            payments_data
        )
        print(f"   ✓ Added {len(payments_data)} payment records")
        
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
        
        # Recent payments
        cur.execute('''
            SELECT t.full_name, p.amount, p.payment_date
            FROM payments p
            JOIN tenants t ON p.tenant_id = t.id
            ORDER BY p.payment_date DESC
            LIMIT 3
        ''')
        recent = cur.fetchall()
        if recent:
            print(f"\n📅 Recent Payments:")
            for name, amount, date in recent:
                print(f"   • {name}: ₱{amount:,.2f} on {date}")
        
        print("\n" + "=" * 50)
        print("✅ Database is ready to use!")
        print(f"📁 Database file: {DB_NAME}")
        print("🚀 Run your main application: python vista_verde.py")
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
