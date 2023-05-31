from models import *

def update_line_items():
    orders = Order.query.all()
    for order in orders:
        line_items = LineItem.query.filter_by(order_id=order.order_id).all()
        shipping_per_item = order.shipping_cost / len(line_items)
        for line_item in line_items:
            line_item.shipping_cost = shipping_per_item
            if line_item.total_amount_paid != 0 and order.total_amount_paid != 0:
                line_item.fees = order.fees / ((order.total_amount_paid) / line_item.total_amount_paid)
            else:
                line_item.fees = 0.00
            db.session.add(line_item)