from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models.closet import ClosetItem

closet_bp = Blueprint('closet', __name__)

@closet_bp.route('/closet/add', methods=['POST'])
@login_required
def add_to_closet():
    title = request.form.get('title')
    price = request.form.get('price')
    image_url = request.form.get('image')

    if title and image_url:
        item = ClosetItem(
            user_id=current_user.id,
            title=title,
            price=price,
            image_url=image_url
        )
        db.session.add(item)
        db.session.commit()
        flash("Item added to your closet!", "success")

    return redirect(request.referrer or url_for('main.home'))

@closet_bp.route('/closet')
@login_required
def view_closet():
    items = ClosetItem.query.filter_by(user_id=current_user.id).all()
    return render_template('closet.html', items=items)
