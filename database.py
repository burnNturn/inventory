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
                        shipping_cost=shipping_label_cost,
                        total_sale_price=order_data.Subtotal.value,
                        tax=total_tax,
                        total_amount_paid=order_data.AmountPaid.value,
                        fees=total_fees)

            # Add the Order instance to the database
            db.session.add(order)

            line_items = order_data.TransactionArray.Transaction
            if not isinstance(line_items, list):
                line_items = [line_items]
            for line_item in line_items:
                print("Creating a line item")
                sku = None
                if hasattr(line_item.Item, 'SKU'):
                    sku = line_item.Item.SKU
                amount_paid = float(line_item.TransactionPrice.value) + float(line_item.ActualShippingCost.value) + float(line_item.Taxes.TaxDetails.TaxAmount.value)
                line_item_fees = 0.00
                if hasattr(line_item, 'Item.SellingStatus.FinalValueFee'):
                    line_item_fees = line_item.Item.SellingStatus.FinalValueFee.value
                line_item_instance = LineItem(line_item_id=line_item.TransactionID,
                                                transaction_date=line_item.CreatedDate,
                                                shipping_cost=0.00,
                                                total_sale_price=line_item.TransactionPrice.value,
                                                tax=line_item.Taxes.TaxDetails.TaxAmount.value,
                                                shipping_charged=line_item.ActualShippingCost.value,
                                                total_amount_paid=amount_paid,
                                                fees=line_item_fees,
                                                order_id=order.order_id,
                                                sku=sku)
                db.session.add(line_item_instance)

                total_tax += float(line_item.Taxes.TaxDetails.TaxAmount.value)
            
                total_fees += line_item_fees

            order.tax = total_tax
            order.fees = total_fees

            # Create Transaction instances and add them to the database
            # for transaction in transaction_data:
            #     transaction_instance = Transaction(id=transaction['id'],
            #                                        transaction_date=transaction['transaction_date'],
            #                                        shipping_cost=transaction['shipping_cost'],
            #                                        total_sale_price=transaction['total_sale_price'],
            #                                        tax=transaction['tax'],
            #                                        total_amount_paid=transaction['total_amount_paid'],
            #                                        fees=transaction['fees'],
            #                                        order_id=order.id)
            #     db.session.add(transaction_instance)



        # Commit the changes to the database
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
    for entry in LineItem.query.all():
        print("LINE ITEM ID:")
        print(entry.line_item_id)

def save_ebay_transactions(transaction_data):
    for transaction in transaction_data:
        print(transaction['TransactionId'])
        line_item_id = transaction['LineItemID']
        print(line_item_id)
        if not Transaction.query.filter_by(transaction_id=transaction['TransactionId'], transaction_type=transaction['TransactionType'], line_item_id=line_item_id).first():
            print('Transaction not found in database. Adding to database.')
            order = Order.query.filter_by(order_id=transaction['OrderID']).first()
            try :
                order_id = order.order_id
            except: 
                order_id = None
            print('Order ID: ', order_id)
            line_item = LineItem.query.filter_by(line_item_id=transaction['LineItemID']).first()
            try:
                print('Line Item ID: ', line_item.line_item_id)
            except:
                print('No line item found')

            transaction_instance = Transaction(transaction_id=transaction['TransactionId'],
                                            transaction_date=transaction['CreatedDate'],
                                            transaction_type=transaction['TransactionType'],
                                            line_item_id=line_item_id,
                                            amount=transaction['Amount'],
                                            booking_entry=transaction['BookingEntry'],
                                            order_id=transaction['OrderID'])
            db.session.add(transaction_instance)
            if transaction_instance.line_item_id != None:
                print("Found a line item")
                if 'FEE' in transaction_instance.transaction_type:
                    print("Found a FEE FEE FEE")
                    if transaction_instance.booking_entry == 'DEBIT':
                        order.fees += float(transaction_instance.amount)
                        if line_item:
                            line_item.fees += float(transaction_instance.amount)
                    elif transaction_instance.booking_entry == 'CREDIT':
                        order.fees -= float(transaction_instance.amount)
                        if line_item:
                            line_item.fees -= float(transaction_instance.amount)
            if order:
                print("Found an order")
                if transaction['TransactionType'] == 'SHIPPING_LABEL':
                    print("Found a shipping label")
                    if transaction['BookingEntry'] == 'DEBIT':
                        print("Found a debit")
                        order.shipping_cost += float(transaction['Amount'])
                    elif transaction['BookingEntry'] == 'CREDIT':
                        print("Found a credit")
                        order.shipping_cost -= float(transaction['Amount'])
        
        update_line_items()

            
        print(" ")
                            
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
