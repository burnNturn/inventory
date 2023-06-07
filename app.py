import pandas as pd
from amazon import get_amazon_sales
from sp_api.base import Marketplaces
from ebay import *

from forms import *
from dotenv import load_dotenv

from database import *
from models import *

load_dotenv()

with app.app_context():
    LineItem.query.delete()
    Order.query.delete()
    Transaction.query.delete()
    Item.query.delete()
    PurchaseLot.query.delete()
    db.session.commit()
    db.create_all()

@app.route('/add-item', methods=['GET', 'POST'])
def add_item():
    print("Adding item...")
    form = ItemForm()
    form.purchase_lot.choices = [(lot.id, lot.lot_identifier) for lot in PurchaseLot.query.all()]  # Populate purchase lot choices
    if form.validate_on_submit():
        purchase_lot_id = form.purchase_lot.data  # Retrieve the selected purchase lot ID
        purchase_lot = PurchaseLot.query.get(purchase_lot_id)  # Get the purchase lot based on the ID
        item = Item(
            purchase_lot_id=purchase_lot.id,
            sku_id=form.sku_id.data,
            title=form.title.data,
            units_received=form.units_received.data,
            cost_per_unit=form.cost_per_unit.data
        )
        print(purchase_lot.lot_identifier + item.sku_id)
        db.session.add(item)
        db.session.commit()
        return redirect(url_for('item_details', item_id=item.id))
    return render_template('add_item.html', form=form)

@app.route('/item/<int:item_id>')
def item_details(item_id):
    item = Item.query.get_or_404(item_id)
    return render_template('item_details.html', item=item)

@app.route('/display-items')
def display_items():
    items = Item.query.all()
    purchase_lots = PurchaseLot.query.all()
    return render_template('display_items.html', items=items, purchase_lots=purchase_lots)

@app.context_processor
def inject_functions():
    def get_purchase_lot_identifier(purchase_lot_id):
        purchase_lot = PurchaseLot.query.get(purchase_lot_id)
        if purchase_lot:
            return purchase_lot.lot_identifier
        return 'N/A'
    
    return dict(get_purchase_lot_identifier=get_purchase_lot_identifier)

@app.route('/display_ebay_sales')
def display_ebay_sales():
    start_date = "2023-06-01T00:00:00.000Z"
    end_date = "2023-06-06T00:00:00.000Z"
    # Fetch data from the eBay API
    raw_xml, order_data, transaction_data = fetch_ebay_data(start_date, end_date)

    # Save the data into the database
    save_ebay_data_to_database(order_data)
    save_ebay_transactions(transaction_data)
    # Query the orders and transactions from the database
    orders = Order.query.all()
    line_items = LineItem.query.all()
    # Render the display_ebay_sales.html template with the orders and transactions data
    return render_template('display_ebay_sales.html', orders=orders, line_items=line_items,  raw_xml=raw_xml)

@app.route('/display_amazon_sales')
def display_amazon_sales():
    start_date = '2023-06-01'  # Replace with the desired start date
    end_date = '2023-06-02'  #')
    sales_data, raw_xml = get_amazon_sales(start_date, end_date)
    return render_template('display_amazon_sales.html', sales_data=sales_data, raw_xml=raw_xml)

@app.route('/display_orders')
def display_orders():
    orders


@app.route('/order_line_items/<order_id>')
def display_order_line_items(order_id):
    order = Order.query.filter_by(order_id=order_id).first()
    line_items = LineItem.query.filter_by(order_id=order_id).all()
    order_items = sum(line_item.quantity for line_item in line_items)
    transactions = Transaction.query.filter_by(order_id=order_id).all()
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
            lot_identifier=form.lot_identifier.data,
            purchase_date=form.purchase_date.data,
            purchase_venue=form.purchase_venue.data,
            venue_transaction_number=form.venue_transaction_number.data,
            origin_vendor=form.origin_vendor.data,
            type=form.type.data,
            main_category=form.main_category.data,
            short_description=form.short_description.data,
            units_received=form.units_received.data,
            subtotal_cost=form.subtotal_cost.data,
            purchase_fees=form.purchase_fees.data,
            inbound_shipping_cost=form.inbound_shipping_cost.data,
            other_cost=form.other_cost.data,
            discounts=form.discounts.data,
            purchase_taxes=form.purchase_taxes.data,
            link_to_purchase_page=form.link_to_purchase_page.data

        )
        db.session.add(purchase_lot)
        db.session.commit()
        return redirect(url_for('purchase_lot_details', purchase_lot_id=purchase_lot.id))
    return render_template('add_purchase_lot.html', form=form)

# Route to display the details of an individual purchase lot
@app.route('/purchase_lot/<int:purchase_lot_id>')
def purchase_lot_details(purchase_lot_id):
    purchase_lot = PurchaseLot.query.get_or_404(purchase_lot_id)
    return render_template('purchase_lot_details.html', purchase_lot=purchase_lot)

@app.route('/display-purchase-lots')
def display_purchase_lots():
    purchase_lots = PurchaseLot.query.all()
    return render_template('display_purchase_lots.html', purchase_lots=purchase_lots)

if __name__ == '__main__':
    app.run(debug=True)

