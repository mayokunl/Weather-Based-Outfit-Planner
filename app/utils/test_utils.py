"""
Test utilities for database operations and data validation.
Contains test functions for verifying database state and category consistency.
"""
import unittest
import logging
from app import create_app, db
from app.models.closet import ClosetItem
from app.models.user import User
from app.utils.database_utils import (
    initialize_database, 
    update_dress_categories, 
    check_database_health,
    get_category_statistics
)

logger = logging.getLogger(__name__)

class DatabaseUtilsTest(unittest.TestCase):
    """Test cases for database utility functions."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test application context."""
        cls.app = create_app()
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test application context."""
        cls.app_context.pop()
    
    def setUp(self):
        """Set up each test case."""
        # Initialize fresh database for each test
        db.create_all()
    
    def tearDown(self):
        """Clean up after each test case."""
        # Clear all data
        db.session.remove()
        db.drop_all()
    
    def test_initialize_database(self):
        """Test database initialization."""
        # Drop tables first
        db.drop_all()
        
        # Test initialization
        result = initialize_database()
        self.assertTrue(result, "Database initialization should succeed")
        
        # Verify tables exist
        with db.engine.connect() as conn:
            result = conn.execute(db.text("SELECT name FROM sqlite_master WHERE type='table';"))
            tables = [row[0] for row in result.fetchall()]
            
            expected_tables = ['user', 'trip', 'closet_item']
            for table in expected_tables:
                self.assertIn(table, tables, f"Table '{table}' should exist")
    
    def test_update_dress_categories(self):
        """Test dress category updates."""
        # Create test user first
        test_user = User(username='testuser', email='test@example.com', password_hash='dummy')
        db.session.add(test_user)
        db.session.commit()
        
        # Create test items with incorrect categories
        test_items = [
            ClosetItem(title='Summer Dress', item_type='dresses', user_id=test_user.id),
            ClosetItem(title='Party Dress', item_type='bottoms', user_id=test_user.id),
            ClosetItem(title='Regular Pants', item_type='bottoms', user_id=test_user.id),
        ]
        
        for item in test_items:
            db.session.add(item)
        db.session.commit()
        
        # Run update function
        updated_count = update_dress_categories()
        
        # Verify updates
        self.assertEqual(updated_count, 2, "Should update 2 items")
        
        # Check specific items
        summer_dress = ClosetItem.query.filter_by(title='Summer Dress').first()
        party_dress = ClosetItem.query.filter_by(title='Party Dress').first()
        regular_pants = ClosetItem.query.filter_by(title='Regular Pants').first()
        
        self.assertEqual(summer_dress.item_type, 'dress')
        self.assertEqual(party_dress.item_type, 'dress')
        self.assertEqual(regular_pants.item_type, 'bottoms')  # Should remain unchanged
    
    def test_check_database_health(self):
        """Test database health check."""
        health = check_database_health()
        
        self.assertTrue(health['database_accessible'], "Database should be accessible")
        self.assertTrue(health['tables_exist'], "Tables should exist")
        self.assertEqual(health['user_count'], 0, "Should start with 0 users")
        self.assertEqual(health['trip_count'], 0, "Should start with 0 trips")
        self.assertEqual(health['closet_item_count'], 0, "Should start with 0 closet items")
        self.assertEqual(len(health['issues']), 0, "Should have no issues")
    
    def test_get_category_statistics(self):
        """Test category statistics function."""
        # Create test user first
        test_user = User(username='testuser', email='test@example.com', password_hash='dummy')
        db.session.add(test_user)
        db.session.commit()
        
        # Create test items
        test_items = [
            ClosetItem(title='T-Shirt', item_type='top', user_id=test_user.id),
            ClosetItem(title='Jeans', item_type='bottom', user_id=test_user.id),
            ClosetItem(title='Dress', item_type='dress', user_id=test_user.id),
            ClosetItem(title='Sneakers', item_type='shoe', user_id=test_user.id),
        ]
        
        for item in test_items:
            db.session.add(item)
        db.session.commit()
        
        # Get statistics
        stats = get_category_statistics()
        
        self.assertNotIn('error', stats, "Should not have errors")
        self.assertEqual(stats['total_items'], 4, "Should have 4 total items")
        self.assertEqual(len(stats['categories']), 4, "Should have 4 different categories")
        self.assertEqual(len(stats['issues']), 0, "Should have no category issues")

def run_validation_tests():
    """
    Run validation tests and return results.
    This can be called from other parts of the application.
    """
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(DatabaseUtilsTest)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2, stream=open('/dev/null', 'w'))
    result = runner.run(suite)
    
    # Return summary
    return {
        'tests_run': result.testsRun,
        'failures': len(result.failures),
        'errors': len(result.errors),
        'success': result.wasSuccessful(),
        'failure_details': [str(failure[1]) for failure in result.failures],
        'error_details': [str(error[1]) for error in result.errors]
    }

def validate_categories():
    """
    Quick validation function to check category consistency.
    Returns True if all categories are properly standardized.
    """
    try:
        stats = get_category_statistics()
        if 'error' in stats:
            logger.error(f"Error getting category statistics: {stats['error']}")
            return False
        
        # Check for problematic categories
        problematic_categories = ['dresses', 'tops', 'bottoms', 'shoes', 'accessories']
        
        issues_found = []
        for category in problematic_categories:
            if category in stats['categories']:
                issues_found.append(f"Found {stats['categories'][category]} items with '{category}' category")
        
        if issues_found:
            logger.warning(f"Category validation issues: {issues_found}")
            return False
        
        logger.info("Category validation passed - all categories properly standardized")
        return True
        
    except Exception as e:
        logger.error(f"Category validation failed: {e}")
        return False

if __name__ == "__main__":
    # Run tests when called directly
    print("Running database utility tests...")
    
    app = create_app()
    with app.app_context():
        # Run validation tests
        results = run_validation_tests()
        
        print(f"\nTest Results:")
        print(f"  Tests run: {results['tests_run']}")
        print(f"  Failures: {results['failures']}")
        print(f"  Errors: {results['errors']}")
        print(f"  Success: {results['success']}")
        
        if results['failure_details']:
            print(f"  Failure details: {results['failure_details']}")
        if results['error_details']:
            print(f"  Error details: {results['error_details']}")
        
        # Run category validation
        print(f"\nCategory validation: {'PASSED' if validate_categories() else 'FAILED'}")
