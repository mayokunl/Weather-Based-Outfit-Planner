"""
Database utilities for initialization, maintenance, and data migration.
Contains functions for setting up the database and maintaining data consistency.
"""
import logging
from app import create_app, db
from app.models.user import User
from app.models.trip import Trip
from app.models.closet import ClosetItem

logger = logging.getLogger(__name__)

def initialize_database():
    """
    Initialize the database with all tables.
    This function should be run when setting up the application for the first time.
    """
    try:
        # Create all tables
        db.create_all()
        logger.info("Database tables created successfully")
        
        # Check if database was properly initialized
        with db.engine.connect() as conn:
            # Test basic table creation
            result = conn.execute(db.text("SELECT name FROM sqlite_master WHERE type='table';"))
            tables = [row[0] for row in result.fetchall()]
            
            expected_tables = ['user', 'trip', 'closet_item']
            missing_tables = [table for table in expected_tables if table not in tables]
            
            if missing_tables:
                logger.error(f"Missing tables: {missing_tables}")
                return False
            
            logger.info(f"Database initialized with tables: {tables}")
            return True
            
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        return False

def update_dress_categories():
    """
    Update any closet items categorized as 'dresses' or 'bottoms' 
    that should be 'dress' category.
    This is a data migration utility.
    """
    try:
        # Find items that need category updates
        items_to_update = ClosetItem.query.filter(
            db.or_(
                db.and_(ClosetItem.item_type == 'dresses'),
                db.and_(ClosetItem.item_type == 'bottoms', ClosetItem.title.ilike('%dress%'))
            )
        ).all()
        
        updated_count = 0
        for item in items_to_update:
            if item.item_type == 'dresses' or 'dress' in item.title.lower():
                item.item_type = 'dress'
                updated_count += 1
        
        if updated_count > 0:
            db.session.commit()
            logger.info(f"Updated {updated_count} items to 'dress' category")
        else:
            logger.info("No items needed category updates")
            
        return updated_count
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to update dress categories: {e}")
        return 0

def check_database_health():
    """
    Perform basic health checks on the database.
    Returns a dictionary with health status information.
    """
    health_status = {
        'database_accessible': False,
        'tables_exist': False,
        'user_count': 0,
        'trip_count': 0,
        'closet_item_count': 0,
        'issues': []
    }
    
    try:
        # Test database connection
        with db.engine.connect() as conn:
            conn.execute(db.text("SELECT 1"))
            health_status['database_accessible'] = True
        
        # Check table existence
        with db.engine.connect() as conn:
            result = conn.execute(db.text("SELECT name FROM sqlite_master WHERE type='table';"))
            tables = [row[0] for row in result.fetchall()]
            
            expected_tables = ['user', 'trip', 'closet_item']
            missing_tables = [table for table in expected_tables if table not in tables]
            
            if not missing_tables:
                health_status['tables_exist'] = True
            else:
                health_status['issues'].append(f"Missing tables: {missing_tables}")
        
        # Get record counts
        if health_status['tables_exist']:
            health_status['user_count'] = User.query.count()
            health_status['trip_count'] = Trip.query.count()
            health_status['closet_item_count'] = ClosetItem.query.count()
        
        logger.info(f"Database health check completed: {health_status}")
        
    except Exception as e:
        health_status['issues'].append(f"Database error: {str(e)}")
        logger.error(f"Database health check failed: {e}")
    
    return health_status

def get_category_statistics():
    """
    Get statistics about closet item categories.
    Useful for monitoring data consistency.
    """
    try:
        # Get category distribution
        category_stats = {}
        
        with db.engine.connect() as conn:
            result = conn.execute(db.text("""
                SELECT item_type, COUNT(*) as count 
                FROM closet_item 
                GROUP BY item_type 
                ORDER BY count DESC
            """))
            
            for row in result.fetchall():
                category_stats[row[0]] = row[1]
        
        # Check for potential category issues
        issues = []
        if 'dresses' in category_stats:
            issues.append(f"Found {category_stats['dresses']} items with 'dresses' category (should be 'dress')")
        
        return {
            'categories': category_stats,
            'total_items': sum(category_stats.values()),
            'issues': issues
        }
        
    except Exception as e:
        logger.error(f"Failed to get category statistics: {e}")
        return {'error': str(e)}

if __name__ == "__main__":
    # Allow running this module directly for database setup
    app = create_app()
    with app.app_context():
        print("Initializing database...")
        if initialize_database():
            print("Database initialized successfully!")
            
            # Run category updates
            print("Updating dress categories...")
            updated = update_dress_categories()
            print(f"Updated {updated} items")
            
            # Show health status
            print("\nDatabase health check:")
            health = check_database_health()
            for key, value in health.items():
                print(f"  {key}: {value}")
                
            # Show category stats
            print("\nCategory statistics:")
            stats = get_category_statistics()
            if 'error' not in stats:
                for category, count in stats['categories'].items():
                    print(f"  {category}: {count}")
                if stats['issues']:
                    print(f"  Issues: {stats['issues']}")
        else:
            print("Failed to initialize database!")
