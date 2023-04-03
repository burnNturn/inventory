import os
import pandas as pd
from datetime import datetime
from ebaysdk.trading import Connection as Trading
from ebaysdk.exception import ConnectionError
import requests
from requests.models import PreparedRequest
import json

from xml.dom.minidom import parseString


trading_api = Trading(
    appid=os.getenv("EBAY_APP_ID"),
    devid=os.getenv("EBAY_DEV_ID"),
    certid=os.getenv("EBAY_CERT_ID"),
    token=os.getenv("EBAY_USER_TOKEN"),
    config_file=None,
    timeout=60  # Increase the timeout value (in seconds)
)

def fetch_ebay_data(start_date, end_date):
    # Replace with your actual eBay API fetching function
    # This example assumes that you have a get_orders() function that returns a list of orders
    # and a get_order_transactions(order_id) function that returns a list of transactions for a given order_id
    raw_xml, orders = get_orders(start_date, end_date)
    errors = []
    all_transactions = []

    """ for order in orders:
        order_id = order.OrderID
        transactions = get_order_transactions(order_id)

        if transactions is not None:
            for transaction in transactions:
                # Add the order_id to the transaction data
                transaction['order_id'] = order_id

            all_transactions.extend(transactions) """
    all_transactions = get_order_transactions(start_date, end_date)

    return raw_xml, orders, all_transactions

def get_orders(start_date, end_date):

    try:
        response = trading_api.execute('GetOrders', {
            'CreateTimeFrom': start_date,
            'CreateTimeTo': end_date,
            'OrderRole': 'Seller',
            'OrderStatus': 'Completed',
            'DetailLevel': 'ReturnAll',
            'Pagination': {'EntriesPerPage': 100, 'PageNumber': 1}
        })

        if response.reply.Ack == 'Success':
            orders = response.reply.OrderArray.Order
            raw_xml = parseString(response.content).toprettyxml()
            return raw_xml, orders
        else:
            print(response.reply.Errors.LongMessage)
            raw_xml = response.text
            return raw_xml, []

    except ConnectionError as e:
        print(f"Error: {e}")
        raw_xml = response.text
        return raw_xml, []


def get_ebay_sales(start_date, end_date):
    try:
        response = trading_api.execute('GetOrders', {
            'CreateTimeFrom': start_date,
            'CreateTimeTo': end_date,
            'OrderRole': 'Seller',
            'OrderStatus': 'Completed',
            'Pagination': {'EntriesPerPage': 100, 'PageNumber': 1}
        })

        if response.reply.Ack == 'Success':
            orders = response.reply.OrderArray.Order
        # else:
        #     print(response.reply.Errors.LongMessage)
        #     return []

        sales_data = []

        for order in orders:
            transactions = order.TransactionArray.Transaction
            if not isinstance(transactions, list):
                transactions = [transactions]

            for transaction in transactions:
                sku = None
                if hasattr(transaction.Item, 'SKU'):
                    sku = transaction.Item.SKU

                sale = {
                    'OrderID': order.OrderID,
                    'TransactionID': transaction.TransactionID,
                    'CreatedDate': transaction.CreatedDate,
                    'ItemSKU': sku,
                }
                sales_data.append(sale)

        return sales_data

    except ConnectionError as e:
        print(f"Error: {e}")
        return []



YOUR_EBAY_AUTH_TOKEN = 'v^1.1#i^1#f^0#p^3#I^3#r^0#t^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'

EBAY_API_ENDPOINT = 'https://apiz.ebay.com/sell/finances/v1/transaction'

def print_request(req: PreparedRequest):
    print(f'{req.method} {req.url}')
    print(f'Headers: {req.headers}')
    print(f'Body: {req.body}')

def get_order_transactions(start_date, end_date):
    headers = {
        'Authorization': f'Bearer {YOUR_EBAY_AUTH_TOKEN}',
        'X-EBAY-C-MARKETPLACE-ID': 'EBAY_US',
        'Content-Type': 'application/json'
    }

    params = {
        #'filter': f'orderId:{{{order_id}}}'
        'filter': f'transactionDate:[{start_date}..{end_date}]'
    }

    req = requests.Request('GET', EBAY_API_ENDPOINT, headers=headers, params=params)
    prepared_req = req.prepare()

    # Print the prepared request for debugging
    print_request(prepared_req)

    response = requests.Session().send(prepared_req)

    print(f"API Response Status Code: {response.status_code}")
    print(f"API Response Headers: {response.headers}")
    print(f"API Response Text: {response.text}")

    if response.status_code == 200:
        try:
            transactions = response.json()['transactions']
        except json.JSONDecodeError:
            print(f"Error: Response is not in JSON format: {response.text}")
            return None

        transactions_data = []

        
        for transaction in transactions:
            order_id = None
            if hasattr(transaction, 'orderId'):
                order_id = transaction['orderId']
            else:
                if hasattr(transaction, 'references'):
                    references = transaction['references']
                    for reference in references:
                        if reference['referenceType'] == 'ORDER_ID':
                            order_id = reference['referenceId']
            line_item_id = None
            if hasattr(transaction, 'orderLineItems'):
                line_items = transaction['orderLineItems']
                for line_item in line_items:
                    line_item_id = line_item['lineItemId']
                    if hasattr(line_item, 'marketplaceFees'):
                        for fee in line_item['marketplaceFees']:
                            transactions_data.append({
                                "TransactionId": transaction['transactionId'],
                                'TransactionType': fee['feeType'],
                                'CreatedDate': pd.to_datetime(transaction['transactionDate']),
                                #'CreatedDate': datetime.strptime(transaction['transactionDate'], '%m/%d/%Y %H:%M:%S %p'),
                                'Amount': fee['value'],
                                'LineItemID': line_item_id,
                                'BookingEntry' : 'DEBIT',
                                'OrderID': order_id,
                            })
            if hasattr(transaction, 'ebayCollectAndRemitTaxes'):
                tax = transaction['ebayCollectAndRemitTaxes']
                transactions_data.append({
                    "TransactionId": transaction['transactionId'],
                    'TransactionType': 'Tax',
                    'CreatedDate': pd.to_datetime(transaction['transactionDate']),
                    'Amount': tax['value'],
                    'LineItemID': None,
                    'BookingEntry' : 'DEBIT',
                    'OrderID': order_id,
                })
            transactions_data.append({
                "TransactionId": transaction['transactionId'],
                'TransactionType': transaction['transactionType'],
                'CreatedDate': pd.to_datetime(transaction['transactionDate']),
                'Amount': transaction['amount']['value'],
                'LineItemID': None,
                'BookingEntry' : transaction['bookingEntry'],
                'OrderID': order_id,
            })

        return transactions_data

    elif response.status_code == 204:
        print("No transactions found for the given dates.")
        return []

    else:
        try:
            error_message = response.json()
        except json.JSONDecodeError:
            error_message = response.text

        print(f"Error: {response.status_code}, {error_message}")
        return None
