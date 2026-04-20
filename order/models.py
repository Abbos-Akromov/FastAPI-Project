from database import Base
from sqlalchemy import String, Text, Numeric, Column, Integer, ForeignKey, DateTime
from datetime import datetime
from sqlalchemy_utils import Choice
from sqlalchemy.orm import relationship

class Products(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    title = Column(String(20))
    desc = Column(Text, nullable=False)
    price = Column(Numeric(10, 2))
    category_id = Column(Integer,ForeignKey('categories.id'))
    user_id = Column(Integer, ForeignKey('user.id'))
    created_at = Column(DateTime, default=datetime.now())

    # category = relationship('Category', back_populates='products')
    order = relationship('Order', back_populates='product')
    user = relationship('User', back_populates='product')

class Card(Base):
    __tablename__ = 'card'
    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey('user.id'), unique=True)

    items = relationship('CardItem', back_populates='card')
    user = relationship('User', back_populates='card')


class CardItem(Base):
    __tablename__ = 'carditem'
    id = Column(Integer, primary_key=True)
    card_id = Column(ForeignKey('card.id'), unique=True)
    product_id = Column(ForeignKey('product.id'))
    quantity = Column(Integer)

    card = relationship('Card', back_populates='items')


class Order(Base):
    STATUS = (
    ('new', 'New'),
    ('in_progress', 'In_progress'),
    ('done', 'Done')
    )
    __tablename__ = 'order'
    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey('user.id'), unique=True)
    status = Column(Choice=STATUS, default='new')

    items_order = relationship('OrderItem', back_populates='order')
    user = relationship('User', back_populates='order')


class OrderItem(Base):
    __tablename__ = 'orderitem'
    id = Column(Integer, primary_key=True)
    order_id = Column(ForeignKey('order.id'), unique=True)
    product_id = Column(ForeignKey('product.id'))
    quantity = Column(Integer)

    order = relationship('Order', back_populates='items_order')





