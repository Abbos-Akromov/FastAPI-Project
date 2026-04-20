from sqlalchemy.orm import relationship

from database import Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    first_name = Column(String(50), nullable=True)
    username = Column(String(50), unique=True)
    email = Column(String(50), unique=True)
    phone_number = Column(String(13), unique=True)
    password = Column(String(250))
    is_staff = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)

    products = relationship('Product', back_populates='user')
    order = relationship('Order', back_populates='order')
    card = relationship('Card', back_populates='Card')



    def __repr__(self):
        return self.username

