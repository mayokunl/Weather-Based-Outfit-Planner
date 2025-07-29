#!/usr/bin/env python3
"""
Database management script for TripStylist application.
Provides command-line interface for database operations.
"""
import sys
import argparse
from app import create_app
from app.utils.database_utils import (
    initialize_database,
    update_dress_categories,
    check_database_health,
    get_category_statistics
)
from app.utils.test_utils import run_validation_tests, validate_categories

def setup_database():
    """Initialize the database and run basic setup."""
    print("Setting up database...")
    
    if initialize_database():
        print("✓ Database initialized successfully")
        
        # Update categories
        print("Updating dress categories...")
        updated = update_dress_categories()
        print(f"✓ Updated {updated} items to correct categories")
        
        # Validate setup
        print("Validating setup...")
        if validate_categories():
            print("✓ Category validation passed")
        else:
            print("⚠ Category validation issues found")
        
        return True
    else:
        print("✗ Failed to initialize database")
        return False

def health_check():
    """Run database health check."""
    print("Running database health check...")
    
    health = check_database_health()
    
    print(f"Database accessible: {'✓' if health['database_accessible'] else '✗'}")
    print(f"Tables exist: {'✓' if health['tables_exist'] else '✗'}")
    print(f"User count: {health['user_count']}")
    print(f"Trip count: {health['trip_count']}")
    print(f"Closet item count: {health['closet_item_count']}")
    
    if health['issues']:
        print("Issues found:")
        for issue in health['issues']:
            print(f"  ⚠ {issue}")
    else:
        print("✓ No issues found")

def show_stats():
    """Show category statistics."""
    print("Category statistics:")
    
    stats = get_category_statistics()
    
    if 'error' in stats:
        print(f"✗ Error: {stats['error']}")
        return
    
    print(f"Total items: {stats['total_items']}")
    print("Categories:")
    for category, count in stats['categories'].items():
        print(f"  {category}: {count}")
    
    if stats['issues']:
        print("Issues:")
        for issue in stats['issues']:
            print(f"  ⚠ {issue}")

def run_tests():
    """Run validation tests."""
    print("Running validation tests...")
    
    results = run_validation_tests()
    
    print(f"Tests run: {results['tests_run']}")
    print(f"Failures: {results['failures']}")
    print(f"Errors: {results['errors']}")
    print(f"Overall: {'✓ PASSED' if results['success'] else '✗ FAILED'}")
    
    if results['failure_details']:
        print("Failure details:")
        for detail in results['failure_details']:
            print(f"  {detail}")
    
    if results['error_details']:
        print("Error details:")
        for detail in results['error_details']:
            print(f"  {detail}")

def main():
    """Main entry point for the database management script."""
    parser = argparse.ArgumentParser(description='TripStylist Database Management')
    
    parser.add_argument('command', choices=['setup', 'health', 'stats', 'test'], 
                       help='Command to run')
    
    args = parser.parse_args()
    
    # Create application context
    app = create_app()
    with app.app_context():
        if args.command == 'setup':
            setup_database()
        elif args.command == 'health':
            health_check()
        elif args.command == 'stats':
            show_stats()
        elif args.command == 'test':
            run_tests()

if __name__ == "__main__":
    main()
