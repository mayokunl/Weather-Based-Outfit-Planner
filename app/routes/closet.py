from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.closet import ClosetItem
from sqlalchemy.exc import IntegrityError

closet_bp = Blueprint('closet', __name__)

def categorize_item(item_name):
    """Automatically categorize clothing items based on keywords."""
    item_lower = item_name.lower()
    
    # Define categories with keywords
    categories = {
        'top': ['shirt', 'blouse', 'top', 'tank', 'tee', 'sweater', 'hoodie', 'cardigan', 'jacket', 'blazer', 'coat'],
        'bottom': ['pants', 'jeans', 'shorts', 'skirt', 'leggings', 'trousers'],
        'dress': ['dress', 'gown', 'frock', 'sundress', 'maxi dress', 'mini dress'],
        'shoe': ['shoes', 'sneakers', 'boots', 'sandals', 'heels', 'flats', 'loafers', 'slip-on'],
        'accessory': ['hat', 'cap', 'sunglasses', 'bag', 'purse', 'backpack', 'scarf', 'belt'],
        'jewelry': ['jewelry', 'watch', 'necklace', 'bracelet', 'ring', 'earrings']
    }
    
    for category, keywords in categories.items():
        if any(keyword in item_lower for keyword in keywords):
            return category
    
    return 'other'  # Default category

@closet_bp.route('/closet/add', methods=['POST'])
@login_required
def add_to_closet():
    title = request.form.get('title')
    price = request.form.get('price')
    image_url = request.form.get('image')
    source = request.form.get('source', 'Unknown Store')
    item_type = request.form.get('item_type')

    if title and image_url:
        # Auto-categorize if no type provided
        if not item_type:
            item_type = categorize_item(title)
        
        # Check if item already exists (duplicate prevention)
        existing_item = ClosetItem.query.filter_by(
            user_id=current_user.id,
            title=title,
            source=source
        ).first()
        
        if existing_item:
            flash(f"'{title}' from {source} is already in your closet!", "info")
        else:
            try:
                item = ClosetItem(
                    user_id=current_user.id,
                    title=title,
                    price=price,
                    image_url=image_url,
                    item_type=item_type,
                    source=source
                )
                db.session.add(item)
                db.session.commit()
                flash(f"Added '{title}' to your {item_type} collection!", "success")
            except IntegrityError:
                db.session.rollback()
                flash("This item is already in your closet!", "info")

    return redirect(request.referrer or url_for('closet.view_closet'))

@closet_bp.route('/closet/remove/<int:item_id>', methods=['POST'])
@login_required
def remove_from_closet(item_id):
    item = ClosetItem.query.filter_by(id=item_id, user_id=current_user.id).first()
    
    if item:
        db.session.delete(item)
        db.session.commit()
        flash(f"Removed '{item.title}' from your closet!", "success")
    else:
        flash("Item not found or you don't have permission to remove it.", "error")
    
    return redirect(url_for('closet.view_closet'))

@closet_bp.route('/closet/update-category/<int:item_id>', methods=['POST'])
@login_required
def update_item_category(item_id):
    """Update the category of a closet item."""
    item = ClosetItem.query.filter_by(id=item_id, user_id=current_user.id).first()
    
    if not item:
        return jsonify({'success': False, 'message': 'Item not found'}), 404
    
    new_category = request.json.get('category', '').strip().lower()
    
    # Validate category
    valid_categories = ['top', 'bottom', 'shoe', 'dress', 'accessory', 'jewelry', 'bag', 'other']
    
    if new_category not in valid_categories:
        return jsonify({'success': False, 'message': 'Invalid category'}), 400
    
    try:
        item.item_type = new_category
        db.session.commit()
        return jsonify({'success': True, 'message': 'Category updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Failed to update category'}), 500

@closet_bp.route('/closet')
@login_required
def view_closet():
    # Get filter parameter
    filter_category = request.args.get('filter', '')
    
    # Get ALL user's items first (to check if they have any items at all)
    all_user_items = ClosetItem.query.filter_by(user_id=current_user.id).all()
    has_any_items = len(all_user_items) > 0
    
    # Get items organized by category (with filter applied)
    query = ClosetItem.query.filter_by(user_id=current_user.id)
    
    if filter_category and filter_category != 'all':
        query = query.filter_by(item_type=filter_category)
    
    items = query.order_by(ClosetItem.item_type, ClosetItem.title).all()
    
    # Group items by category
    items_by_category = {}
    for item in items:
        category = item.item_type or 'other'
        if category not in items_by_category:
            items_by_category[category] = []
        items_by_category[category].append(item)
    
    # Define standard categories (same as dropdown options)
    standard_categories = ['top', 'bottom', 'dress', 'shoe', 'accessory', 'jewelry', 'other']
    
    # Always show all standard categories as filter options
    return render_template('closet.html', 
                         items_by_category=items_by_category, 
                         total_items=len(items),
                         all_categories=standard_categories,
                         current_filter=filter_category,
                         has_any_items=has_any_items,
                         total_user_items=len(all_user_items))
