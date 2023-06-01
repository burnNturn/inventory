from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from enum import Enum
from sqlalchemy import Enum as EnumSQL




app = Flask(__name__)
app.config['SECRET_KEY'] = '55ab57607aabbbfebdba19058e3f3ce9'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///purchase_lots.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True


db = SQLAlchemy(app)
migrate = Migrate(app, db)


class PurchaseLotType(Enum):
    ONLINE_ARBITRAGE = 'Online Arbitrage'
    RETAIL_ARBITRAGE = 'Retail Arbitrage'
    LIQUIDATION = 'Liquidation'
    WHOLESALE = 'Wholesale'
    THRIFT = 'Thrift'
    OTHER = 'Other'






class PurchaseLot(db.Model):
    __tablename__ = 'purchase_lots'

    items = db.relationship('Item', backref='purchase_lot', lazy=True)
    #items = db.relationship('Item', backref='purchase_lot', lazy=True, foreign_keys='Item.purchase_lot_id')
    #purchase_lot_id = db.Column(db.Integer, db.ForeignKey('purchase_lots.id', name='fk_item_purchase_lot_id'), nullable=False)

    id = db.Column(db.Integer, primary_key=True)
    lot_identifer = db.Column(db.String(255), nullable=False, unique=True)
    purchase_date = db.Column(db.Date, nullable=False)
    purchase_venue = db.Column(db.String(255), nullable=False)
    venue_transaction_number = db.Column(db.String(255), nullable=True)
    origin_vendor = db.Column(db.String(255), nullable=False)
    type = db.Column(EnumSQL(PurchaseLotType), nullable=False)
    cost = db.Column(db.Float, nullable=False)
    main_category = db.Column(db.String(255), nullable=False)
    short_description = db.Column(db.String(255), nullable=True)
    units_received = db.Column(db.Integer, nullable=True)
    units_sold = db.Column(db.Integer, nullable=False, default=0)
    subtotal_cost = db.Column(db.Float, nullable=False, default=0.00)
    purchase_fees = db.Column(db.Float, nullable=False, default=0.00)
    inbound_shipping_cost = db.Column(db.Float, nullable=False, default=0.00)
    other_cost = db.Column(db.Float, nullable=False, default=0.00)
    discounts = db.Column(db.Float, nullable=False, default=0.00)
    purchase_taxes = db.Column(db.Float, nullable=False, default=0.00)
    link_to_purchase_page = db.Column(db.String(255), nullable=True)
    
    @property
    def total_purchase_cost(self):
        return self.subtotal_cost + self.purchase_fees + self.inbound_shipping_cost + self.other_cost + self.discounts + self.purchase_taxes
    @property
    def subtotal_sales(self):
        return sum([(item.total_sale_price * item.quantity) for item in self.items])
    
    @property
    def outbound_shipping_charged(self):
        return sum([(item.shipping_charged) for item in self.items])
    @property
    def sale_taxes(self):
            return sum([item.tax for item in self.items])
    @property
    def gross_revenue(self):
        return self.subtotal_sales + self.outbound_shipping_charged + self.sale_taxes
    @property
    def outbound_shipping_cost(self):
        return sum([item.shipping_cost for item in self.items])
    @property
    def sale_fees(self):
        return sum([item.fees for item in self.items])
    @property
    def net_revenue(self):
        return self.gross_revenue - self.outbound_shipping_cost - self.sale_fees - self.sale_taxes
    @property
    def profit_loss_dol(self):
        return self.net_revenue - self.total_purchase_cost
    @property
    def profit_loss_per(self):
        return self.profit_loss_dol / self.total_purchase_cost
    
    @property
    def units_remaining(self):
        return self.units_received - self.units_sold

    
    
    

    def __repr__(self):
        return f'<PurchaseLot {self.lot_identifer}>'
    

class Item(db.Model):
    __tablename__ = 'items'

    purchase_lot_id = db.Column(db.Integer, db.ForeignKey('purchase_lots.id'), nullable=True)
    #purchase_lot_id = db.Column(db.Integer, db.ForeignKey('purchase_lots.id', name='fk_line_item_purchase_lot_id'), nullable=True)
    lineItems = db.relationship('LineItem', backref='item', lazy=True)

    id = db.Column(db.Integer, primary_key=True)
    sku_id = db.Column(db.String(255), nullable=False, unique=True)
    title = db.Column(db.String(255), nullable=False)
    units_received = db.Column(db.Integer, nullable=False, default=0)
    cost_per_unit = db.Column(db.Float, nullable=False)
    
    @property
    def units_sold(self):
        return sum([line_item.quantity for line_item in self.lineItems])
    @property
    def average_sale_price(self):
        return sum([line_item.total_sale_price for line_item in self.lineItems]) / self.units_sold
    @property
    def shipping_charged(self):
        return sum([line_item.total_shipping_charged for line_item in self.lineItems])
    @property
    def sale_taxes(self):
        return sum([lineitem.tax for lineitem in self.lineItems])
    @property
    def gross_revenue(self):
        return sum([line_item.total_amount_paid for line_item in self.lineItems])
    @property
    def sale_fees(self):
        return sum([line_item.fees for line_item in self.lineItems])
    @property
    def outbound_shipping_cost(self):
        return sum([line_item.shipping_cost for line_item in self.lineItems])
    @property
    def net_revenue(self):
        return self.revenue - self.shipping_charged - self.sale_fees - self.sale_taxes
    @property
    def profit_loss_dol(self):
        return self.net_revenue - (self.cost_per_unit * self.units_sold)
    @property
    def profit_loss_per(self):
        return self.profit_loss_dol / (self.cost_per_unit * self.units_sold)

    def __repr__(self):
        return f'<Item {self.sku_id}>'

class LineItem(db.Model):
    __tablename__ = 'line_items'

    id = db.Column(db.Integer, primary_key=True)
    line_item_id = db.Column(db.String, nullable=False, unique=True)
    transaction_date = db.Column(db.Date, nullable=False)
    sku = db.Column(db.String, default=None)
    quantity = db.Column(db.Integer, nullable=False)
    shipping_cost = db.Column(db.Float, nullable=False, default=0.00)
    total_sale_price = db.Column(db.Float, nullable=False, default=0.00)
    shipping_charged = db.Column(db.Float, nullable=False, default=0.00)
    tax = db.Column(db.Float, nullable=False, default=0.00)
    total_amount_paid = db.Column(db.Float, nullable=False, default=0.00)
    fees = db.Column(db.Float, nullable=False, default=0.00)


    order_id = db.Column(db.String, db.ForeignKey('orders.order_id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=True)
    #order = db.relationship('Order', back_populates='line_items')



class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.String, nullable=False, unique=True)
    order_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    order_venue = db.Column(db.String, nullable=False)
    _shipping_cost = db.Column(db.Float, nullable=False, default=0.00)
    _fees = db.Column(db.Float, nullable=False, default=0.00)

    @property
    def shipping_cost(self):
        return self._shipping_cost

    @shipping_cost.setter
    def shipping_cost(self, shipping_cost):
        self._shipping_cost = shipping_cost
        self.update_line_item_shipping_cost()

    def update_line_item_shipping_cost(self):
        print("GOT HERE!!!!!!!!!!!!!!!!!!")
        line_items = LineItem.query.filter_by(order_id=self.order_id).all()
        if self.quantity > 0:
            ship_cost = self._shipping_cost / self.quantity
        else:
            ship_cost = 0.00
        for line_item in line_items:
            line_item.shipping_cost = ship_cost * line_item.quantity
        db.session.commit()

    @property
    def fees(self):
        return self._fees

    @fees.setter
    def fees(self, fees):
        self._fees = fees
        self.update_line_item_fees()

    def update_line_item_fees(self):
        line_items = LineItem.query.filter_by(order_id=self.order_id).all()
        for line_item in line_items:
            if line_item.total_amount_paid != 0 and self.total_amount_paid != 0:
                line_item.fees = self._fees / ((self.total_amount_paid) / line_item.total_amount_paid)
            else:
                line_item.fees = 0.00
        db.session.commit()
    
    @property
    def quantity(self):
        return sum([line_item.quantity for line_item in self.lineItems])
    @property
    def total_sale_price(self):
        return sum([(line_item.total_sale_price * line_item.quantity) for line_item in self.lineItems])
    @property
    def shipping_charged(self):
        return sum([line_item.shipping_charged for line_item in self.lineItems])
    @property
    def tax(self):
        return sum([line_item.tax for line_item in self.lineItems])
    @property
    def total_amount_paid(self):
        return sum([line_item.total_amount_paid for line_item in self.lineItems])
    @property
    def net_revenue(self):
        return self.total_amount_paid - self.shipping_cost - self.fees - self.tax


    lineItems = db.relationship('LineItem', backref='order', lazy=True)
    orderTransactions = db.relationship('Transaction', backref='order', lazy=True)

class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.String, nullable=False, unique=False)
    line_item_id = db.Column(db.String)
    transaction_date = db.Column(db.DateTime, nullable=False)
    transaction_type = db.Column(db.String, nullable=False)
    amount = db.Column(db.Float, nullable=False, default=0.00)
    booking_entry = db.Column(db.String, nullable=False)

    order_id = db.Column(db.String, db.ForeignKey('orders.order_id'))
