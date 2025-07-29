"""
Utility modules for the TripStylist application.

Contains:
- helpers.py: Parsing utilities for outfit recommendations
- shared_utils.py: Error handling decorators and centralized messages
- database_utils.py: Database initialization and maintenance functions
- test_utils.py: Test utilities for validation and testing
"""

# Import commonly used utilities for easier access
from .helpers import parse_daily_outfits, extract_clothing_items
from .shared_utils import (
    handle_database_errors, 
    handle_route_errors, 
    ErrorMessages, 
    SuccessMessages
)
from .database_utils import (
    initialize_database,
    update_dress_categories, 
    check_database_health,
    get_category_statistics
)
from .test_utils import validate_categories, run_validation_tests

__all__ = [
    # Helpers
    'parse_daily_outfits',
    'extract_clothing_items',
    
    # Shared utilities
    'handle_database_errors',
    'handle_route_errors', 
    'ErrorMessages',
    'SuccessMessages',
    
    # Database utilities
    'initialize_database',
    'update_dress_categories',
    'check_database_health',
    'get_category_statistics',
    
    # Test utilities
    'validate_categories',
    'run_validation_tests'
]
