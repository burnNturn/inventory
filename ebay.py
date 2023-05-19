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



YOUR_EBAY_AUTH_TOKEN = 'v^1.1#i^1#f^0#r^0#p^3#I^3#t^H4sIAAAAAAAAAOVZa2xbVx2P7SSolLbQDYYqhly3PLrq2ue+/LjEFk6ch5M4dmM3ZRGddXzvufaJ78O559zYjjQpikYnlSE2GBITH6gY0zQqIRCoCCoeG0iFwVQqxIYmmDR1pWOaNBgSkfKhcK/zqJtpbRPngyXuF/uc83/9/q9zz7lgqX/PA2fGzqzs83zAe24JLHk9HnYv2NPfd3y/z3uorwe0EXjOLR1d6l32vTlAoK7VpGlEaqZBkL+hawaRWpPxgG0ZkgkJJpIBdUQkKkv5ZGZS4oJAqlkmNWVTC/jTqXiACyOIQBSykFfCUbHkzBobMgtmPFACUFE4rgShzJd4FHXWCbFR2iAUGtThBxzPAIFhxQLHSWxEEsUgH+ZnA/4ZZBFsGg5JEAQSLXOlFq/VZuvtTYWEIIs6QgKJdHIkn02mU8NThYFQm6zEuh/yFFKb3DoaMhXkn4GajW6vhrSopbwty4iQQCixpuFWoVJyw5gdmN9ydaQElRjPQyUsK5GYWtoVV46Ylg7p7e1wZ7DCqC1SCRkU0+adPOp4ozSHZLo+mnJEpFN+9+eEDTWsYmTFA8ODyQdP5oenA/58LmeZC1hBSiupBA5EOV7gw4HEAipDUiwjA1lQW1e0Jm3dzVs0DZmGgl2nEf+USQeRYzXa6hvQ5huHKGtkraRKXYs26cIFADZ8KEZn3aCuRdGmFcONK9IdR/hbwztHYCMlbibBbiUFq0YcDbEYDyCvcjHwnqRwa30HiZFwY5PM5UKuLagEm4wOrSqiNQ3KiJEd99o6srAi8aLK8VEVMUo4pjJCTFWZkqiEGVZFCCBUKsmx6P9TflBq4ZJN0WaObF1ogYwH8rJZQzlTw3IzsJWk1XPWM6JB4oEKpTUpFKrX68E6HzStcogDgA19ITOZlytIh4FNWnxnYga3ckNGDhfBEm3WHGsaTuo5yo1yIMFbSg5atJlHmuZMbCTuLbYlts6+D8ghDTseKDgqugvjmEkoUjqCpqAFLKMiVroImVvrDjoOxMJiWIgJLmtHIDWzjI0MohWzm2A6EEez2dHJ4Y6wOU0U0u5C1daFWHG9CwEhyjj/AOgIbLJWS+u6TWFJQ+kui6UQ4SOC0BE8d4OSMFQlalaR0X39Znp4ZHo4P1YsZCeGpzpCOo1UC5FKwXRr3cHabcFMnkimk86TyeZpIyOqo7lS9FRj6MFUoZyx1OTMIDreYAU9MzOei0ZHK+U8n+Ln68kIP8Eu6np91JqYXAQKR6dOxOMdOSqPZAt1WX2nx/FYWqgYmtKYqdQXJ3BOnx8jgxP4RGlcyFUbE2ToFL8wNjmSyXQGPlPuqn1pV/ekQneWuLVWmMVWByo6o45ADpfttgi6td4VIBFC4TDPs2xEBjASQbwSFaPOS76qqjIXViIdYa7Z3Za0yjwvC1ZZt4rNjnffLoM2ZFrNqTShTNpYcF7RTYvJTaeYGFJBhAMyx0RVhWeFmNwRbuKecboLt8tPHAGwhoPuW0NQNvWQCZ1jvDtVbFnsvxuiEHHOR8G1Q7EjOWghqJiG1twJczuPW+t34MPrIWvuROkm8zZ4oCybtkF3om6ddRscqq2pWNPco/NOFLaxb8dMA2pNimWyI5XYcDOObIOlBpstgAomNbde7orTmdORJaMgVtYu4bZp7Ca/YVKsYhm61yBBYpeIbOFa6xZql+RsGtbZCQ0p2EIyLdoW7q4u4nbPots+NWQxW1opA405Wb8r4L3L3uvvB971eTeevNOpXTjFpNBCt22ISJblqKjKDAeiAiOoImBgSRAYRWF5XhV54Kx3hLnrbhvYcJQVYxEQ4e8W15aJtivO99xuh279vJToaT3ssucFsOz5hdfjAQPgU+wRcLjfd7LX96FDBFOnr0E1SHDZgNS2ULCKmjWILe89PSvg+rfkt8eeO1u9UZ//++ce7mn/unXuNPj45vetPT52b9vHLvCJmyt97IH79nE8EFiR49iIKM6CIzdXe9mP9d77ymzo3OvLh7/z+r+ujfs+/KXjVDs9APZtEnk8fT29y56eg8/M/mnl/v+mjo1e+OcbX/7Z6tevzJ0cuLxy9bo4c+rPmSvjRe6GMH/trYMPzTyduDjbf+D3z2MrGf9hMr/4mje4Ov/Wj/yX/vK37/X/1fvE1I/3v/uVbOi7n/nkT3/nJy8++pz2mHf1P0B59fI72sPPL/780jt4/xd9daXy2pELsYtXHsf3V8/a737+a74Xjn+/z/PBo8ZTg28+0ryQvXiv/rT1255CIPXNh1bePvYY+s1XH1kVfll5NnWo+hMcO3q11kAvDf0q98bVnpHzz75ywJfX79l7/dLLjw6+9I1rj3/2zLerT/7xyeq/K8kf2PelnvnH0kdXPzJ3/vDVV59q7Jk7e/APkvrr0APL5298+uUXT18+Rtdi+T/37aRddxwAAA=='

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
            print("Got Here")
            order_id = None
            if 'orderId' in transaction:
                print("Found order id: " + transaction['orderId'])
                order_id = transaction['orderId']
            else:
                if 'references' in transaction:
                    references = transaction['references']
                    for reference in references:
                        if reference['referenceType'] == 'ORDER_ID':
                            print("Found reference order id: " + reference['referenceId'])
                            order_id = reference['referenceId']
            line_item_id = None
            if 'orderLineItems' in transaction:
                print("Found order line items:")
                line_items = transaction['orderLineItems']
                for line_item in line_items:
                    print("Found line item id: " + line_item['lineItemId'])
                    line_item_id = line_item['lineItemId']
                    print("Found line item id: " + line_item_id)
                    if 'marketplaceFees' in line_item:
                        for fee in line_item['marketplaceFees']:
                            transactions_data.append({
                                "TransactionId": transaction['transactionId'],
                                'TransactionType': fee['feeType'],
                                'CreatedDate': pd.to_datetime(transaction['transactionDate']),
                                #'CreatedDate': datetime.strptime(transaction['transactionDate'], '%m/%d/%Y %H:%M:%S %p'),
                                'Amount': fee['amount']['value'],
                                'LineItemID': line_item_id,
                                'BookingEntry' : 'DEBIT',
                                'OrderID': order_id,
                            })
            if 'ebayCollectAndRemitTaxes' in transaction:
                tax = transaction['ebayCollectAndRemitTaxes']
                transactions_data.append({
                    "TransactionId": transaction['transactionId'],
                    'TransactionType': 'Tax',
                    'CreatedDate': pd.to_datetime(transaction['transactionDate']),
                    'Amount': tax['value'],
                    'LineItemID': line_item_id,
                    'BookingEntry' : 'DEBIT',
                    'OrderID': order_id,
                })
            transactions_data.append({
                "TransactionId": transaction['transactionId'],
                'TransactionType': transaction['transactionType'],
                'CreatedDate': pd.to_datetime(transaction['transactionDate']),
                'Amount': transaction['amount']['value'],
                'LineItemID': line_item_id,
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
