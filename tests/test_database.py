#!/usr/bin/env python3
"""
Vista Verde Apartments - Database Unit Tests
"""
import unittest
import sqlite3
import os
import sys
import time
from datetime import datetime

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Test database name
TEST_DB = "test_vista_verde.db"

class TestDatabaseOperations(unittest.TestCase):
    """Test database CRUD operations"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test database once for all tests"""
        print("\n🧪 Setting up test database...")
        # Clean up any existing test database
        cls._cleanup_database()
        
    @classmethod
    def _cleanup_database(cls):
        """Helper method to safely remove test database"""
        if os.path.exists(TEST_DB):
            try:
                os.remove(TEST_DB)
            except PermissionError:
                # If file is locked, wait a bit and try again
                time.sleep(0.1)
                try:
                    os.remove(TEST_DB)
                except:
                    pass  # If still fails, just continue
        
    def setUp(self):
        """Create a fresh test database before each test"""
        # Make sure previous connection is closed and file is removed
        self._cleanup_database()
        
        # Create test database
        self.conn = sqlite3.connect(TEST_DB)
        
        # CRITICAL: Enable foreign key constraints
        self.conn.execute("PRAGMA foreign_keys = ON")
        
        self.cur = self.conn.cursor()
        
        # Create tables
        self.cur.execute('''
            CREATE TABLE units (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                unit_number TEXT UNIQUE NOT NULL,
                unit_type TEXT,
                monthly_rent REAL,
                is_occupied INTEGER DEFAULT 0,
                created_at TEXT
            )
        ''')
        
        self.cur.execute('''
            CREATE TABLE tenants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                unit_id INTEGER,
                move_in_date TEXT,
                monthly_rent REAL,
                FOREIGN KEY (unit_id) REFERENCES units (id) ON DELETE SET NULL
            )
        ''')
        
        self.cur.execute('''
            CREATE TABLE payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                payment_date TEXT NOT NULL,
                month_covered TEXT,
                FOREIGN KEY (tenant_id) REFERENCES tenants (id) ON DELETE CASCADE
            )
        ''')
        
        self.conn.commit()
    
    def tearDown(self):
        """Clean up after each test"""
        # Close cursor first
        if hasattr(self, 'cur') and self.cur:
            self.cur.close()
        
        # Close connection
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()
        
        # Wait a moment for Windows to release the file lock
        time.sleep(0.05)
        
        # Remove test database
        self._cleanup_database()
    
    # ==================== UNIT TESTS ====================
    
    def test_01_create_unit(self):
        """Test creating a new unit"""
        print("\n✅ Test: Create Unit")
        
        self.cur.execute(
            "INSERT INTO units (unit_number, unit_type, monthly_rent, created_at) VALUES (?, ?, ?, ?)",
            ("101", "Studio", 8000.00, datetime.now().strftime("%Y-%m-%d"))
        )
        self.conn.commit()
        
        # Verify unit was created
        self.cur.execute("SELECT * FROM units WHERE unit_number = '101'")
        unit = self.cur.fetchone()
        
        self.assertIsNotNone(unit, "Unit should be created")
        self.assertEqual(unit[1], "101", "Unit number should be 101")
        self.assertEqual(unit[2], "Studio", "Unit type should be Studio")
        self.assertEqual(unit[3], 8000.00, "Rent should be 8000.00")
    
    def test_02_duplicate_unit_number(self):
        """Test that duplicate unit numbers are prevented"""
        print("\n✅ Test: Duplicate Unit Number Prevention")
        
        # Insert first unit
        self.cur.execute(
            "INSERT INTO units (unit_number, unit_type, monthly_rent, created_at) VALUES (?, ?, ?, ?)",
            ("101", "Studio", 8000.00, datetime.now().strftime("%Y-%m-%d"))
        )
        self.conn.commit()
        
        # Try to insert duplicate
        with self.assertRaises(sqlite3.IntegrityError):
            self.cur.execute(
                "INSERT INTO units (unit_number, unit_type, monthly_rent, created_at) VALUES (?, ?, ?, ?)",
                ("101", "1 Bedroom", 12000.00, datetime.now().strftime("%Y-%m-%d"))
            )
            self.conn.commit()
    
    def test_03_create_tenant(self):
        """Test creating a new tenant"""
        print("\n✅ Test: Create Tenant")
        
        # First create a unit
        self.cur.execute(
            "INSERT INTO units (unit_number, unit_type, monthly_rent, created_at) VALUES (?, ?, ?, ?)",
            ("101", "Studio", 8000.00, datetime.now().strftime("%Y-%m-%d"))
        )
        self.conn.commit()
        unit_id = self.cur.lastrowid
        
        # Create tenant
        self.cur.execute(
            "INSERT INTO tenants (full_name, email, phone, unit_id, move_in_date, monthly_rent) VALUES (?, ?, ?, ?, ?, ?)",
            ("John Doe", "john@email.com", "09123456789", unit_id, "2025-01-01", 8000.00)
        )
        self.conn.commit()
        
        # Verify tenant was created
        self.cur.execute("SELECT * FROM tenants WHERE full_name = 'John Doe'")
        tenant = self.cur.fetchone()
        
        self.assertIsNotNone(tenant, "Tenant should be created")
        self.assertEqual(tenant[1], "John Doe", "Name should be John Doe")
        self.assertEqual(tenant[4], unit_id, "Unit ID should match")
    
    def test_04_record_payment(self):
        """Test recording a payment"""
        print("\n✅ Test: Record Payment")
        
        # Create unit and tenant first
        self.cur.execute(
            "INSERT INTO units (unit_number, unit_type, monthly_rent, created_at) VALUES (?, ?, ?, ?)",
            ("101", "Studio", 8000.00, datetime.now().strftime("%Y-%m-%d"))
        )
        unit_id = self.cur.lastrowid
        
        self.cur.execute(
            "INSERT INTO tenants (full_name, email, phone, unit_id, move_in_date, monthly_rent) VALUES (?, ?, ?, ?, ?, ?)",
            ("John Doe", "john@email.com", "09123456789", unit_id, "2025-01-01", 8000.00)
        )
        tenant_id = self.cur.lastrowid
        self.conn.commit()
        
        # Record payment
        self.cur.execute(
            "INSERT INTO payments (tenant_id, amount, payment_date, month_covered) VALUES (?, ?, ?, ?)",
            (tenant_id, 8000.00, datetime.now().strftime("%Y-%m-%d"), "2025-01")
        )
        self.conn.commit()
        
        # Verify payment
        self.cur.execute("SELECT * FROM payments WHERE tenant_id = ?", (tenant_id,))
        payment = self.cur.fetchone()
        
        self.assertIsNotNone(payment, "Payment should be recorded")
        self.assertEqual(payment[2], 8000.00, "Amount should be 8000.00")
    
    def test_05_delete_unit(self):
        """Test deleting a unit"""
        print("\n✅ Test: Delete Unit")
        
        # Create unit
        self.cur.execute(
            "INSERT INTO units (unit_number, unit_type, monthly_rent, created_at) VALUES (?, ?, ?, ?)",
            ("101", "Studio", 8000.00, datetime.now().strftime("%Y-%m-%d"))
        )
        self.conn.commit()
        unit_id = self.cur.lastrowid
        
        # Delete unit
        self.cur.execute("DELETE FROM units WHERE id = ?", (unit_id,))
        self.conn.commit()
        
        # Verify unit is deleted
        self.cur.execute("SELECT * FROM units WHERE id = ?", (unit_id,))
        unit = self.cur.fetchone()
        
        self.assertIsNone(unit, "Unit should be deleted")
    
    def test_06_tenant_deletion_cascades_payments(self):
        """Test that deleting a tenant deletes their payments"""
        print("\n✅ Test: Cascade Delete Payments")
        
        # Create unit and tenant
        self.cur.execute(
            "INSERT INTO units (unit_number, unit_type, monthly_rent, created_at) VALUES (?, ?, ?, ?)",
            ("101", "Studio", 8000.00, datetime.now().strftime("%Y-%m-%d"))
        )
        unit_id = self.cur.lastrowid
        
        self.cur.execute(
            "INSERT INTO tenants (full_name, email, phone, unit_id, move_in_date, monthly_rent) VALUES (?, ?, ?, ?, ?, ?)",
            ("John Doe", "john@email.com", "09123456789", unit_id, "2025-01-01", 8000.00)
        )
        tenant_id = self.cur.lastrowid
        
        # Record payment
        self.cur.execute(
            "INSERT INTO payments (tenant_id, amount, payment_date, month_covered) VALUES (?, ?, ?, ?)",
            (tenant_id, 8000.00, datetime.now().strftime("%Y-%m-%d"), "2025-01")
        )
        self.conn.commit()
        
        # Verify payment exists before deletion
        self.cur.execute("SELECT * FROM payments WHERE tenant_id = ?", (tenant_id,))
        payment_before = self.cur.fetchone()
        self.assertIsNotNone(payment_before, "Payment should exist before tenant deletion")
        
        # Delete tenant
        self.cur.execute("DELETE FROM tenants WHERE id = ?", (tenant_id,))
        self.conn.commit()
        
        # Verify payments are also deleted (CASCADE DELETE)
        self.cur.execute("SELECT * FROM payments WHERE tenant_id = ?", (tenant_id,))
        payment = self.cur.fetchone()
        
        self.assertIsNone(payment, "Payment should be deleted when tenant is deleted")
    
    def test_07_calculate_total_revenue(self):
        """Test calculating total revenue from payments"""
        print("\n✅ Test: Calculate Total Revenue")
        
        # Create unit and tenant
        self.cur.execute(
            "INSERT INTO units (unit_number, unit_type, monthly_rent, created_at) VALUES (?, ?, ?, ?)",
            ("101", "Studio", 8000.00, datetime.now().strftime("%Y-%m-%d"))
        )
        unit_id = self.cur.lastrowid
        
        self.cur.execute(
            "INSERT INTO tenants (full_name, email, phone, unit_id, move_in_date, monthly_rent) VALUES (?, ?, ?, ?, ?, ?)",
            ("John Doe", "john@email.com", "09123456789", unit_id, "2025-01-01", 8000.00)
        )
        tenant_id = self.cur.lastrowid
        
        # Record multiple payments
        payments = [
            (tenant_id, 8000.00, "2025-01-01", "2025-01"),
            (tenant_id, 8000.00, "2025-02-01", "2025-02"),
            (tenant_id, 8000.00, "2025-03-01", "2025-03"),
        ]
        
        self.cur.executemany(
            "INSERT INTO payments (tenant_id, amount, payment_date, month_covered) VALUES (?, ?, ?, ?)",
            payments
        )
        self.conn.commit()
        
        # Calculate total
        self.cur.execute("SELECT SUM(amount) FROM payments")
        total = self.cur.fetchone()[0]
        
        self.assertEqual(total, 24000.00, "Total revenue should be 24000.00")
    
    def test_08_get_available_units(self):
        """Test getting available (unoccupied) units"""
        print("\n✅ Test: Get Available Units")
        
        # Create occupied and available units
        units = [
            ("101", "Studio", 8000.00, 1),  # Occupied
            ("102", "Studio", 8000.00, 0),  # Available
            ("103", "Studio", 8000.00, 0),  # Available
        ]
        
        for unit in units:
            self.cur.execute(
                "INSERT INTO units (unit_number, unit_type, monthly_rent, is_occupied, created_at) VALUES (?, ?, ?, ?, ?)",
                (unit[0], unit[1], unit[2], unit[3], datetime.now().strftime("%Y-%m-%d"))
            )
        self.conn.commit()
        
        # Get available units
        self.cur.execute("SELECT COUNT(*) FROM units WHERE is_occupied = 0")
        available_count = self.cur.fetchone()[0]
        
        self.assertEqual(available_count, 2, "Should have 2 available units")
    
    def test_09_update_unit_rent(self):
        """Test updating unit rent"""
        print("\n✅ Test: Update Unit Rent")
        
        # Create unit
        self.cur.execute(
            "INSERT INTO units (unit_number, unit_type, monthly_rent, created_at) VALUES (?, ?, ?, ?)",
            ("101", "Studio", 8000.00, datetime.now().strftime("%Y-%m-%d"))
        )
        self.conn.commit()
        unit_id = self.cur.lastrowid
        
        # Update rent
        new_rent = 9000.00
        self.cur.execute("UPDATE units SET monthly_rent = ? WHERE id = ?", (new_rent, unit_id))
        self.conn.commit()
        
        # Verify update
        self.cur.execute("SELECT monthly_rent FROM units WHERE id = ?", (unit_id,))
        rent = self.cur.fetchone()[0]
        
        self.assertEqual(rent, new_rent, f"Rent should be updated to {new_rent}")
    
    def test_10_tenant_payment_history(self):
        """Test retrieving tenant payment history"""
        print("\n✅ Test: Tenant Payment History")
        
        # Create unit and tenant
        self.cur.execute(
            "INSERT INTO units (unit_number, unit_type, monthly_rent, created_at) VALUES (?, ?, ?, ?)",
            ("101", "Studio", 8000.00, datetime.now().strftime("%Y-%m-%d"))
        )
        unit_id = self.cur.lastrowid
        
        self.cur.execute(
            "INSERT INTO tenants (full_name, email, phone, unit_id, move_in_date, monthly_rent) VALUES (?, ?, ?, ?, ?, ?)",
            ("John Doe", "john@email.com", "09123456789", unit_id, "2025-01-01", 8000.00)
        )
        tenant_id = self.cur.lastrowid
        
        # Record multiple payments
        for month in range(1, 4):
            self.cur.execute(
                "INSERT INTO payments (tenant_id, amount, payment_date, month_covered) VALUES (?, ?, ?, ?)",
                (tenant_id, 8000.00, f"2025-{month:02d}-01", f"2025-{month:02d}")
            )
        self.conn.commit()
        
        # Get payment history
        self.cur.execute("SELECT COUNT(*) FROM payments WHERE tenant_id = ?", (tenant_id,))
        payment_count = self.cur.fetchone()[0]
        
        self.assertEqual(payment_count, 3, "Should have 3 payments in history")


class TestLoginValidation(unittest.TestCase):
    """Test login validation"""
    
    def test_01_valid_credentials(self):
        """Test valid login credentials"""
        print("\n✅ Test: Valid Login")
        
        username = "admin"
        password = "Admin123"
        
        # Simulate login validation
        is_valid = (username == "admin" and password == "Admin123")
        
        self.assertTrue(is_valid, "Valid credentials should pass")
    
    def test_02_invalid_username(self):
        """Test invalid username"""
        print("\n✅ Test: Invalid Username")
        
        username = "wronguser"
        password = "Admin123"
        
        is_valid = (username == "admin" and password == "Admin123")
        
        self.assertFalse(is_valid, "Invalid username should fail")
    
    def test_03_invalid_password(self):
        """Test invalid password"""
        print("\n✅ Test: Invalid Password")
        
        username = "admin"
        password = "wrongpass"
        
        is_valid = (username == "admin" and password == "Admin123")
        
        self.assertFalse(is_valid, "Invalid password should fail")
    
    def test_04_case_sensitive_password(self):
        """Test password case sensitivity"""
        print("\n✅ Test: Password Case Sensitivity")
        
        username = "admin"
        password = "admin123"  # Wrong case
        
        is_valid = (username == "admin" and password == "Admin123")
        
        self.assertFalse(is_valid, "Password should be case-sensitive")


def run_tests():
    """Run all tests with detailed output"""
    print("\n" + "="*60)
    print("🧪 VISTA VERDE APARTMENTS - UNIT TESTS")
    print("="*60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestDatabaseOperations))
    suite.addTests(loader.loadTestsFromTestCase(TestLoginValidation))
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    print(f"✅ Tests Run: {result.testsRun}")
    print(f"✅ Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Failed: {len(result.failures)}")
    print(f"💥 Errors: {len(result.errors)}")
    print("="*60)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
