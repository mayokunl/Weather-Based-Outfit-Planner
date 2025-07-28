#!/usr/bin/env python3
"""
Test runner for the Weather-Based Outfit Planner application.
Run all unit tests with: python run_tests.py
"""
import unittest
import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def run_tests():
    """Discover and run all tests in the tests directory."""
    # Discover tests
    loader = unittest.TestLoader()
    test_suite = loader.discover('tests', pattern='test_*.py')
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Return exit code based on test results
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    exit_code = run_tests()
    sys.exit(exit_code)
