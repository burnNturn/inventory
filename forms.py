from flask_wtf import FlaskForm
from wtforms import StringField, DateField, FloatField
from wtforms.validators import DataRequired

class PurchaseLotForm(FlaskForm):
    purchase_date = DateField('Purchase Date', validators=[DataRequired()])
    purchase_venue = StringField('Purchase Venue', validators=[DataRequired()])
    origin_vendor = StringField('Origin Vendor', validators=[DataRequired()])
    lot_sku_id = StringField('Lot SKU ID', validators=[DataRequired()])
    cost = FloatField('Cost', validators=[DataRequired()])
    short_description = StringField('Short Description')
    main_category = StringField('Main Category', validators=[DataRequired()])
    venue_transaction_number = StringField('Venue Transaction Number')
