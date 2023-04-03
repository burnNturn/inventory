from models import *

def save_ebay_data_to_database(orders_data):

    for order_data in orders_data:
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
            sku = None
            if hasattr(line_item.Item, 'SKU'):
                sku = line_item.Item.SKU
            amount_paid = 0.00
            if hasattr(line_item, 'AmountPaid'):
                amount_paid = line_item.AmountPaid.value
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
    db.session.commit()

def save_ebay_transactions(transaction_data):
    print(transaction_data)
    for transaction in transaction_data:
        print(transaction['TransactionId'])
        if not Transaction.query.filter_by(transaction_id=transaction['TransactionId'], transaction_type=transaction['TransactionType'], line_item_id=transaction['LineItemID']).first():
            print('Transaction not found')
            transaction_instance = Transaction(transaction_id=transaction['TransactionId'],
                                            transaction_date=transaction['CreatedDate'],
                                            transaction_type=transaction['TransactionType'],
                                            line_item_id=transaction['LineItemID'],
                                            amount=transaction['Amount'],
                                            booking_entry=transaction['BookingEntry'],
                                            order_id=transaction['OrderID'])
            db.session.add(transaction_instance)

            order = Order.query.filter_by(order_id=transaction['OrderID']).first()
            order_line_items = LineItem.query.filter_by(order.order_id).all()
            
            if transaction.transaction_type == 'SHIPPING_LABEL':
                if transaction.booking_entry == 'DEBIT':
                    order.shipping_cost += float(transaction.amount)
                elif transaction.booking_entry == 'CREDIT':
                    order.shipping_cost -= float(transaction.amount)

                for line_item in order_line_items:
                    line_item.shipping_cost += order.shipping_cost / len(order_line_items)

            line_item = LineItem.query.filter_by(line_item_id=transaction['line_item_id']).first()
            if transaction.transaction_type == 'FEE':
                if transaction.booking_entry == 'DEBIT':
                    order.fees += float(transaction.amount)
                    line_item.fees += float(transaction.amount)
                elif transaction.booking_entry == 'CREDIT':
                    order.fees -= float(transaction.amount)
                    line_item.fees -= float(transaction.amount)
    db.session.commit()
