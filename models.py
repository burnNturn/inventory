from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

app = Flask(__name__)
app.config['SECRET_KEY'] = '55ab57607aabbbfebdba19058e3f3ce9'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///purchase_lots.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)
migrate = Migrate(app, db)


class PurchaseLot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    purchase_date = db.Column(db.Date, nullable=False)
    purchase_venue = db.Column(db.String(255), nullable=False)
    origin_vendor = db.Column(db.String(255), nullable=False)
    lot_sku_id = db.Column(db.String(255), nullable=False)
    cost = db.Column(db.Float, nullable=False)
    short_description = db.Column(db.String(255), nullable=True)
    main_category = db.Column(db.String(255), nullable=False)
    venue_transaction_number = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f'<PurchaseLot {self.lot_sku_id}>'

class LineItem(db.Model):
    __tablename__ = 'line_items'

    id = db.Column(db.Integer, primary_key=True)
    line_item_id = db.Column(db.String, nullable=False, unique=True)
    transaction_date = db.Column(db.Date, nullable=False)
    sku = db.Column(db.String, default=None)
    shipping_cost = db.Column(db.Float, nullable=False, default=0.00)
    total_sale_price = db.Column(db.Float, nullable=False, default=0.00)
    shipping_charged = db.Column(db.Float, nullable=False, default=0.00)
    tax = db.Column(db.Float, nullable=False, default=0.00)
    total_amount_paid = db.Column(db.Float, nullable=False, default=0.00)
    fees = db.Column(db.Float, nullable=False, default=0.00)

    order_id = db.Column(db.String, db.ForeignKey('orders.order_id'), nullable=False)
    #order = db.relationship('Order', back_populates='line_items')



class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.String, nullable=False, unique=True)
    order_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    shipping_cost = db.Column(db.Float, nullable=False, default=0.00)
    total_sale_price = db.Column(db.Float, nullable=False, default=0.00)
    tax = db.Column(db.Float, nullable=False, default=0.00)
    total_amount_paid = db.Column(db.Float, nullable=False, default=0.00)
    fees = db.Column(db.Float, nullable=False, default=0.00)

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
