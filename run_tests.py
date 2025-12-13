#!/usr/bin/env python3
"""
Vista Verde Apartments - Test Runner
Run all unit tests for the system
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import and run tests
from tests.test_database import run_tests

if __name__ == "__main__":
    print("\n🚀 Starting Vista Verde RMS Unit Tests...")
    print("=" * 60)
    
    success = run_tests()
    
    if success:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please check the output above.")
        sys.exit(1)
