from models import *
from helper import *

def save_ebay_data_to_database(orders_data):

    for order_data in orders_data:
        if not Order.query.filter_by(order_id=order_data.OrderID).first():
            shipping_label_cost = 0.00
            total_tax = 0.00
            total_fees = 0.00
            # Create an Order instance

            order = Order(order_id=order_data.OrderID,
                        order_date=order_data.CreatedTime,
                        order_venue='eBay',
                        shipping_cost=shipping_label_cost,
                        fees=total_fees)

            # Add the Order instance to the database
            db.session.add(order)

            line_items = order_data.TransactionArray.Transaction
            if not isinstance(line_items, list):
                line_items = [line_items]
            for line_item in line_items:
                sku = None
                if hasattr(line_item.Item, 'SKU'):
                    sku = line_item.Item.SKU
                amount_paid = (float(line_item.TransactionPrice.value) * int(line_item.QuantityPurchased)) + float(line_item.ActualShippingCost.value) + float(line_item.Taxes.TaxDetails.TaxAmount.value)
                line_item_fees = 0.00
                if hasattr(line_item, 'Item.SellingStatus.FinalValueFee'):
                    line_item_fees = line_item.Item.SellingStatus.FinalValueFee.value
                line_item_instance = LineItem(line_item_id=line_item.TransactionID,
                                                transaction_date=line_item.CreatedDate,
                                                quantity=line_item.QuantityPurchased,
                                                shipping_cost=0.00,
                                                total_sale_price=line_item.TransactionPrice.value,
                                                tax=line_item.Taxes.TaxDetails.TaxAmount.value,
                                                shipping_charged=line_item.ActualShippingCost.value,
                                                total_amount_paid=amount_paid,
                                                fees=line_item_fees,
                                                order_id=order.order_id,
                                                sku=sku)
                db.session.add(line_item_instance)
            
                total_fees += line_item_fees

            order.fees = total_fees

            # Add the Order instance to the database
    try:
       
        #db.session.flush()  # flush the changes to the database
        num_transactions = len(db.session.new)  # get the number of new transactions added
        db.session.commit()  # commit the changes to the database
        print(f"{num_transactions} transactions were added to the database.")  # print the number of new transactions added
    except Exception as e:
        db.session.rollback()
        print(f'Commit failed with error: {e}')
    finally:
        db.session.close()    


def save_ebay_transactions(transaction_data):
    for transaction in transaction_data:
        line_item_id = transaction['LineItemID']
        if not Transaction.query.filter_by(transaction_id=transaction['TransactionId'], transaction_type=transaction['TransactionType'], line_item_id=line_item_id).first():
            order = Order.query.filter_by(order_id=transaction['OrderID']).first()
            try :
                order_id = order.order_id
            except: 
                order_id = None
            line_item = LineItem.query.filter_by(line_item_id=transaction['LineItemID']).first()

            transaction_instance = Transaction(transaction_id=transaction['TransactionId'],
                                            transaction_date=transaction['CreatedDate'],
                                            transaction_type=transaction['TransactionType'],
                                            line_item_id=line_item_id,
                                            amount=transaction['Amount'],
                                            booking_entry=transaction['BookingEntry'],
                                            order_id=transaction['OrderID'])
            db.session.add(transaction_instance)
            if transaction_instance.line_item_id != None or transaction_instance.transaction_type == 'NON_SALE_CHARGE':
                if 'FEE' in transaction_instance.transaction_type or transaction_instance.transaction_type == 'NON_SALE_CHARGE':
                    if transaction_instance.booking_entry == 'DEBIT':
                        order.fees = order.fees + float(transaction_instance.amount)
                        #if line_item:
                            #line_item.fees += float(transaction_instance.amount)
                    elif transaction_instance.booking_entry == 'CREDIT':
                        order.fees = order.fees - float(transaction_instance.amount)
                        #if line_item:
                            #line_item.fees -= float(transaction_instance.amount)
            if order:
                if transaction['TransactionType'] == 'SHIPPING_LABEL':
                    if transaction['BookingEntry'] == 'DEBIT':
                        order.shipping_cost = order.shipping_cost + float(transaction['Amount'])
                    elif transaction['BookingEntry'] == 'CREDIT':
                        order.shipping_cost = order.shipping_cost - float(transaction['Amount'])
        
        
        #update_line_items()

                            
    try:
       
        #db.session.flush()  # flush the changes to the database
        num_transactions = len(db.session.new)  # get the number of new transactions added
        db.session.commit()  # commit the changes to the database
        print(f"{num_transactions} transactions were added to the database.")  # print the number of new transactions added
    except Exception as e:
        db.session.rollback()
        print(f'Commit failed with error: {e}')
    finally:
        db.session.close()   
