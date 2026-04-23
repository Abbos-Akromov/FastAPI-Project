from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from order.schema import CardItemSchema, CardItemUpdateSchema
from order.models import OrderItem, Order, Card, CardItem, Products
from users.models import User
from fastapi_jwt_auth import AuthJWT

router = APIRouter(prefix='/order', tags=['order'])


@router.post('/add_card/{product_id}')
def add_card(product_id: int, data: CardItemSchema, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
        current_user_id = Authorize.get_jwt_subject()

        user = db.query(User).filter(User.id == current_user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User topilmadi")

        card = db.query(Card).filter(Card.user_id == user.id).first()
        if not card:
            card = Card(user_id=user.id)
            db.add(card)
            db.commit()
            db.refresh(card)

        product = db.query(Products).filter(Products.id == product_id).first()
        if not product:
            raise HTTPException(detail='Mahsulot topilmadi', status_code=status.HTTP_404_NOT_FOUND)

        product_card = db.query(CardItem).filter(
            CardItem.product_id == product.id,
            CardItem.card_id == card.id
        ).first()

        if product_card:
            product_card.quantity += data.quantity
            message = 'Maxsulot miqdori yangilandi'
        else:
            product_card = CardItem(
                card_id=card.id,
                product_id=product.id,
                quantity=data.quantity
            )
            db.add(product_card)
            message = 'Maxsulot savatchaga qo\'shildi'

        db.commit()
        return {"status": "success", "message": message}

    except Exception as e:
        db.rollback()
        raise HTTPException(detail=str(e), status_code=status.HTTP_400_BAD_REQUEST)


@router.delete('/delete-card-item/{item_id}')
def delete_card_item(item_id: int, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
        current_user_id = Authorize.get_jwt_subject()

        item = db.query(CardItem).join(Card).filter(
            CardItem.id == item_id,
            Card.user_id == current_user_id
        ).first()

        if not item:
            raise HTTPException(status_code=404, detail="Element topilmadi yoki sizga tegishli emas")

        db.delete(item)
        db.commit()
        return {"status": "success", "message": "Mahsulot savatchadan o'chirildi"}

    except Exception as e:
        db.rollback()
        raise HTTPException(detail=str(e), status_code=status.HTTP_400_BAD_REQUEST)


@router.post('/create-order')
def create_order(db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
        current_user_id = Authorize.get_jwt_subject()

        user = db.query(User).filter(User.id == current_user_id).first()
        card = db.query(Card).filter(Card.user_id == user.id).first()

        if not card or not card.items:
            raise HTTPException(status_code=400, detail="Savatchangiz bo'sh")

        new_order = Order(user_id=user.id, status="pending")
        db.add(new_order)
        db.commit()
        db.refresh(new_order)

        for item in card.items:
            order_item = OrderItem(
                order_id=new_order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                price=item.product.price
            )
            db.add(order_item)
            db.delete(item)

        db.commit()
        return {"status": "success", "order_id": new_order.id}

    except Exception as e:
        db.rollback()
        raise HTTPException(detail=str(e), status_code=status.HTTP_400_BAD_REQUEST)


@router.post('/order/{order_id}/cancel')
def cancel_order(order_id: int, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
        user_id = Authorize.get_jwt_subject()

        order = db.query(Order).filter(Order.id == order_id, Order.user_id == user_id).first()

        if not order:
            raise HTTPException(status_code=404, detail="Buyurtma topilmadi")

        if order.status != "pending":
            raise HTTPException(status_code=400, detail="Faqat kutilayotgan buyurtmalarni bekor qilish mumkin")

        order.status = "canceled"
        db.commit()
        return {"status": "success", "message": "Buyurtma bekor qilindi"}

    except Exception as e:
        db.rollback()
        raise HTTPException(detail=str(e), status_code=status.HTTP_400_BAD_REQUEST)


@router.patch('/order/{order_id}/update-status')
def update_order_status(order_id: int, status_name: str, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()

        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Buyurtma topilmadi")

        order.status = status_name
        db.commit()
        return {"status": "success", "new_status": status_name}

    except Exception as e:
        db.rollback()
        raise HTTPException(detail=str(e), status_code=status.HTTP_400_BAD_REQUEST)
