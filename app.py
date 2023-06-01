import pandas as pd
from amazon import get_amazon_sales
from sp_api.base import Marketplaces
from ebay import *

from forms import PurchaseLotForm
from dotenv import load_dotenv

from database import *
from models import *

load_dotenv()

with app.app_context():
    LineItem.query.delete()
    Order.query.delete()
    Transaction.query.delete()
    db.session.commit()
    db.create_all()

@app.route('/display_ebay_sales')
def display_ebay_sales():
    start_date = "2023-03-15T00:00:00.000Z"
    end_date = "2023-03-30T00:00:00.000Z"
    # Fetch data from the eBay API
    print("Fetching data from eBay API...")
    raw_xml, order_data, transaction_data = fetch_ebay_data(start_date, end_date)

    # Save the data into the database
    print("Saving data to database...")
    save_ebay_data_to_database(order_data)
    print("Saving transactions to database...")
    save_ebay_transactions(transaction_data)
    print("Done saving data to database.")
    # Query the orders and transactions from the database
    orders = Order.query.all()
    line_items = LineItem.query.all()
    # Render the display_ebay_sales.html template with the orders and transactions data
    return render_template('display_ebay_sales.html', orders=orders, line_items=line_items,  raw_xml=raw_xml)


@app.route('/order_line_items/<order_id>')
def display_order_line_items(order_id):
    order = Order.query.filter_by(order_id=order_id).first()
    line_items = LineItem.query.filter_by(order_id=order_id).all()
    order_items = sum(line_item.quantity for line_item in line_items)
    transactions = Transaction.query.filter_by(order_id=order_id).all()
    print(transactions)
    return render_template('display_order_line_items.html', line_items=line_items or [], transactions=transactions or [], order=order, order_items=order_items)

@app.route('/order_transactions/<order_id>')
def display_order_transactions(order_id):
    transactions = get_order_transactions(order_id)
    return render_template('display_order_transactions.html', transactions=transactions or [], order_id=order_id)

@app.route('/amazon-sales')
def amazon_sales():
    start_date = '2023-03-20'  # Replace with the desired start date
    end_date = '2023-03-23'  # Replace with the desired end date
    marketplace_id = Marketplaces.US.marketplace_id
    sales_data = get_amazon_sales(start_date, end_date, marketplace_id)
    return render_template('amazon_sales.html', sales_data=sales_data)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    uploaded_file = request.files['file']
    if uploaded_file.filename != '':
        sales_data = pd.read_csv(uploaded_file)
        # Process the sales data and calculate performance
        # ...
    return 'File uploaded and processed.'

@app.route('/add-purchase-lot', methods=['GET', 'POST'])
def add_purchase_lot():
    form = PurchaseLotForm()
    if form.validate_on_submit():
        purchase_lot = PurchaseLot(
            purchase_date=form.purchase_date.data,
            purchase_venue=form.purchase_venue.data,
            origin_vendor=form.origin_vendor.data,
            lot_sku_id=form.lot_sku_id.data,
            cost=form.cost.data,
            short_description=form.short_description.data,
            main_category=form.main_category.data,
            venue_transaction_number=form.venue_transaction_number.data
        )
        db.session.add(purchase_lot)
        db.session.commit()
        return redirect(url_for('display_purchase_lots'))
    return render_template('add_purchase_lot.html', form=form)

@app.route('/display-purchase-lots')
def display_purchase_lots():
    purchase_lots = PurchaseLot.query.all()
    return render_template('display_purchase_lots.html', purchase_lots=purchase_lots)

if __name__ == '__main__':
    app.run(debug=True)

if __name__ == '__main__':
    app.run(debug=True)
