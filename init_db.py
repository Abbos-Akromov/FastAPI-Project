from database import Base, engine
from users.models import User
from order.models import Products, Order, Card, OrderItem, CardItem

Base.metadata.create_all(bind=engine)

