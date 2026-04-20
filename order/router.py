from fastapi import APIRouter, Depends, status
from database import get_db
from order.schema import CardItemSchema
from sqlalchemy.orm import Session
from fastapi.exceptions import HTTPException
from fastapi_jwt_auth import AuthJWT
from order.models import OrderItem, Order, Card, CardItem
from users.models import User


router = APIRouter(prefix='/order', tags=['order'])


@router.post('/add_card')
def add_card(data: CardItemSchema, db: Session = Depends(get_db()), Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
        current_user = Authorize.get_jwt_subject()
        user = db.query(User).filter(id=current_user).first()

        if user.card:
            card = db.query(Card).filter(user_id=user.id).first()
        else:
            card = Card(user=user)
            db.add(card)
            db.commit()
            db.refresh(card)

        item = Card(user=user, product_id=data.product_id, quantity = data.quantity)

        db.add(item)
        db.commit()
        db.refresh(item)

        data = {
            'status': status.HTTP_201_CREATED,
            'message': 'maxsulot qoshildi'
        }
        return data

    except Exception as e:
        raise HTTPException(detail=str(e), status_code=status.HTTP_400_BAD_REQUEST)



@router.post('/create-order')
def create_order(db: Session = Depends(get_db()), Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
        current_user = Authorize.get_jwt_subject()
        user = db.query(User).filter(id=current_user).first()

        order = Order(user=user.id)

        for i in user.card.items:
            item = OrderItem(**i)

            db.add(item)
            db.commit()
            db.refresh(item)


        db.close()

    except Exception as e:
        raise HTTPException(detail=str(e), status_code=status.HTTP_400_BAD_REQUEST)



