import re
from datetime import date

from models import *
from helper import *
from ebay import *

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
                item_id = get_item("EBAY", sku, line_item.Item.ItemID)
                amount_paid = (Decimal(line_item.TransactionPrice.value) * int(line_item.QuantityPurchased)) + Decimal(line_item.ActualShippingCost.value) + Decimal(line_item.Taxes.TaxDetails.TaxAmount.value)
                line_item_fees = 0.00
                if hasattr(line_item, 'Item.SellingStatus.FinalValueFee'):
                    line_item_fees = line_item.Item.SellingStatus.FinalValueFee.value
                line_item_instance = LineItem(line_item_id=line_item.TransactionID,
                                                item_id=item_id,
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
                        order.fees = order.fees + Decimal(transaction_instance.amount)
                        #if line_item:
                            #line_item.fees += Decimal(transaction_instance.amount)
                    elif transaction_instance.booking_entry == 'CREDIT':
                        order.fees = order.fees - Decimal(transaction_instance.amount)
                        #if line_item:
                            #line_item.fees -= Decimal(transaction_instance.amount)
            if order:
                if transaction['TransactionType'] == 'SHIPPING_LABEL':
                    if transaction['BookingEntry'] == 'DEBIT':
                        order.shipping_cost = order.shipping_cost + Decimal(transaction['Amount'])
                    elif transaction['BookingEntry'] == 'CREDIT':
                        order.shipping_cost = order.shipping_cost - Decimal(transaction['Amount'])
        
        
        #update_line_items()

                            
    try:
       
        #db.session.flush()  # flush the changes to the database
        num_transactions = len(db.session.new)  # get the number of new transactions added
        db.session.commit()  # commit the changes to the database
    except Exception as e:
        db.session.rollback()
        print(f'Commit failed with error: {e}')
    finally:
        db.session.close()   

def get_item(sale_venue, item_sku, item_id):
    print("")
    print(f'Getting item: {item_sku}')
    item = Item.query.filter_by(sku=item_sku).first()
    if item is None:
        item = Item.query.filter_by(sku=item_id).first()
    print(f'Item: {item}')
    
    if item:
        print(f'Item already exists: {item.id}')
        return item.id
    else:
        print(f'Item does not exist: {item_sku}')
        item_instance = save_item(sale_venue, item_sku, item_id)
        print(f'Item saved: {item_instance.sku} as {item_instance.id}')
        return item_instance.id

def save_item(sale_venue, item_sku, item_id):
    if sale_venue == 'EBAY':
        raw_data, item_data = get_ebay_item(item_id)
        purchase_lot_identifier = None
        sku = None
        sku_id = None
        if item_sku is not None:
            sku = item_sku
            sku_list = item_sku.split('-')
            if len(sku_list) >= 2:
                # checks if the first part of the SKU is a single letter followed by a number ex. A103
                # if so, it is assumed to be the purchase lot identifier
                if bool(re.match(r'^[A-Za-z]\d*$', sku_list[0])):
                    purchase_lot_identifier = sku_list[0]
                try:
                    sku_id = int(sku_list[-1])
                except:
                    sku_id = None
            elif len(sku_list) == 1:
                try:
                    sku_id = int(sku_list[0])
                except:
                    sku_id = None
        else:
            sku = item_id
            sku_id = None
            purchase_lot_identifier = None

        purchase_lot_id = None
        purchase_lot = PurchaseLot.query.filter_by(lot_identifier=purchase_lot_identifier).first()

        if purchase_lot:
            print(f'Purchase lot already exists: {purchase_lot.id}')
            purchase_lot_id = purchase_lot.id
        elif purchase_lot_identifier is not None:
            purchase_lot = PurchaseLot(lot_identifier=purchase_lot_identifier,
                            purchase_date=date.today(),
                            purchase_venue="",
                            origin_vendor="",
                            type=PurchaseLotType.OTHER,
                            main_category="")
            purchase_lot_id = purchase_lot.id
            db.session.add(purchase_lot)
            db.session.flush()
        else:
            purchase_lot_id = None
        print(f'Purchase Lot ID: {purchase_lot_id}')
        print(f'SKU: {sku}')
        item = Item(purchase_lot_id=purchase_lot_id,
                        sku_id=sku_id,
                        sku=sku,
                        title=item_data.Title,
                        cost_per_unit=0.00


        )
        
    db.session.add(item)
    db.session.flush()
    if purchase_lot:
        print(f'Purchase Lot: {purchase_lot.lot_identifier}')
        print(f'Gross Revenue: {purchase_lot.gross_revenue}')
        print("")
    return item



