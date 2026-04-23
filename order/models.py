from database import Base
from sqlalchemy import String, Text, Numeric, Column, Integer, ForeignKey, DateTime
from datetime import datetime
from sqlalchemy_utils import ChoiceType
from sqlalchemy.orm import relationship

class Products(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    title = Column(String(50))
    desc = Column(Text, nullable=True)
    price = Column(Numeric(10, 2))
    user_id = Column(Integer, ForeignKey('user.id'))
    created_at = Column(DateTime, default=datetime.now)

    user = relationship('User', back_populates='product')
    card_items = relationship('CardItem', back_populates='product')
    order_items = relationship('OrderItem', back_populates='product')


class Card(Base):
    __tablename__ = 'card'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), unique=True)

    items = relationship('CardItem', back_populates='card')
    user = relationship('User', back_populates='card')


class CardItem(Base):
    __tablename__ = 'carditem'
    id = Column(Integer, primary_key=True)
    card_id = Column(Integer, ForeignKey('card.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer, default=1)

    card = relationship('Card', back_populates='items')
    product = relationship('Products', back_populates='card_items')


class Order(Base):
    STATUS = (
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('done', 'Done')
    )
    __tablename__ = 'order'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    status = Column(ChoiceType(STATUS), default='new')
    created_at = Column(DateTime, default=datetime.now)

    items_order = relationship('OrderItem', back_populates='order')
    user = relationship('User', back_populates='order')


class OrderItem(Base):
    __tablename__ = 'orderitem'
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('order.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer)

    order = relationship('Order', back_populates='items_order')
    product = relationship('Products', back_populates='order_items')
