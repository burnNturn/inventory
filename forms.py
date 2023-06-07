from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SelectField, IntegerField, FloatField
from wtforms.validators import DataRequired

from models import *

class PurchaseLotForm(FlaskForm):
    lot_identifier = StringField('Lot Identifer', validators=[DataRequired()])
    purchase_date = DateField('Purchase Date', validators=[DataRequired()])
    purchase_venue = StringField('Purchase Venue', validators=[DataRequired()])
    venue_transaction_number = StringField('Venue Transaction Number')
    origin_vendor = StringField('Origin Vendor', validators=[DataRequired()])
    type = SelectField('Type', choices=[('ONLINE_ARBITRAGE', 'Online Arbitrage'),
                                        ('RETAIL_ARBITRAGE', 'Retail Arbitrage'),
                                        ('LIQUIDATION', 'Liquidation'),
                                        ('WHOLESALE', 'Wholesale'),
                                        ('THRIFT', 'Thrift'),
                                        ('OTHER', 'Other')],
                       validators=[DataRequired()])
    main_category = StringField('Main Category', validators=[DataRequired()])
    short_description = StringField('Short Description')
    units_received = StringField('Units Received')
    subtotal_cost = StringField('Subtotal Cost')
    purchase_fees = StringField('Purchase Fees')
    inbound_shipping_cost = StringField('Inbound Shipping Cost')
    other_cost = StringField('Other Cost')
    discounts = StringField('Discounts')
    purchase_taxes = StringField('Purchase Taxes')
    link_to_purchase_page = StringField('Link to Purchase Page')

class ItemForm(FlaskForm):
    purchase_lot = SelectField('Purchase Lot', coerce=int, validators=[DataRequired()])
    sku_id = StringField('SKU ID', validators=[DataRequired()])
    title = StringField('Title', validators=[DataRequired()])
    units_received = IntegerField('Units Received', validators=[DataRequired()])
    cost_per_unit = FloatField('Cost per Unit', validators=[DataRequired()])

    """ def __init__(self, *args, **kwargs):
        super(ItemForm, self).__init__(*args, **kwargs)
        self.purchase_lot_id.choices = [(lot.id, lot.lot_identifier) for lot in PurchaseLot.query.all()] """


