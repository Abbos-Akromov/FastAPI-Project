from os import access

from sqlalchemy.testing.plugin.plugin_base import exclude_tags
from users.models import User
from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from users.schemas import SignUpSchema, LoginSchema, UpdateUserSchema, PassUpdateSchema
from sqlalchemy.orm import Session
from database import engine, SessionLocal
from werkzeug.security import generate_password_hash, check_password_hash
from fastapi_jwt_auth import AuthJWT
from sqlalchemy import or_

ACCESS_EXPIRE_TIME = 1
REFRESH_EXPIRE_TIME = 4



router = APIRouter(prefix='/auth', tags=['auth', ])

session = Session(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post('/sign-up', status_code=status.HTTP_201_CREATED)
def sign_up(user: SignUpSchema, db: Session = Depends(get_db)):

    session_username = session.query(User).filter(User.username == user.username).first()

    if session_username:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Bu usernaame band')

    session_email = session.query(User).filter(User.email == user.email).first()
    if session_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Bu email avval royxatdan otgan')

    user = User(
        username = user.username,
        first_name = user.first_name,
        email = user.email,
        password = generate_password_hash(user.password)
    )

    session.add(user)
    session.commit()
    session.close()
    session.refresh(user)

    response = {
        'status': status.HTTP_201_CREATED,
        'message': "User yaratildi",
        'data':{
            'username': user.username,
            'first_name': user.first_name,
            'email': user.email,
        }
    }

    return response


@router.post('/login', status_code=200)
def login(
        data: LoginSchema,
        Authorize: AuthJWT = Depends(),
        db: Session = Depends(get_db)
):
    db_user = session.query(User).filter(or_(User.username == data.username_or_email) | or_(User.email == data.username_or_email)).first()

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Bu username topilmadi'
        )

    if not check_password_hash(db_user.password, data.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Parol xato'
        )

    expires = datetime.timedelta(days=1)
    access_token = Authorize.create_access_token(subject=str(db_user.id), expires_time=expires)
    refresh_token = Authorize.create_refresh_token(subject=str(db_user.id))

    return {
        'message': 'login',
        'access': access_token,
        'refresh': refresh_token
    }





@router.get('/profile')
def profile(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
        current_user = Authorize.get_jwt_subject()
        user = session.query(User).filter(User.id==current_user).first()
        return {
            'status': status.HTTP_200_OK,
            'username': user.username
        }
    except Exception as e:
        raise HTTPException(detail=f'Error: {e}', status_code=status.HTTP_400_BAD_REQUEST)


@router.patch('/update')
def update(new_data: UpdateUserSchema, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
        current_user = Authorize.get_jwt_subject()
        user = session.query(User).filter(User.id==current_user).first()

        if new_data.username:
            user.username = new_data.username
        if new_data.first_name:
            user.first_name = new_data.first_name
        if new_data.email:
            user.email = new_data.email


        session.commit()
        session.refresh(user)

        return {
            'status': status.HTTP_200_OK,
            'username': user.username
        }

    except Exception as e:
        raise HTTPException(detail=f'Error: {e}', status_code=status.HTTP_400_BAD_REQUEST)


@router.patch('/pass-update')
def passwordupdate(data: PassUpdateSchema, Authorize: AuthJWT = Depends()):

    try:
        Authorize.jwt_required()
        current_user = Authorize.get_jwt_subject()
        user = session.query(User).filter(User.id==current_user).first()

        check_user = check_password_hash(user.password, data.old_password)

        if not check_user:
            raise HTTPException(detail='oldingi parol xato', status_code=status.HTTP_400_BAD_REQUEST)

        if data.old_password == data.new_password:
            raise HTTPException(detail = 'Yangi parol oldingisi bilan bir xil bolmasin', status_code=status.HTTP_400_BAD_REQUEST)

        if data.confirm_password != data.new_password:
            raise HTTPException(detail='Yangi parollar bir xil bolishi kerak!', status_code=status.HTTP_400_BAD_REQUEST)

        user.password = generate_password_hash(data.new_password)


        session.commit()
        session.refresh(user)

        return {
            'status': status.HTTP_200_OK,
            'message': 'parol ozgardi'
        }
    except Exception as e:
        raise HTTPException(detail=f'Error: {e}', status_code=status.HTTP_400_BAD_REQUEST)


@router.get('/login_refresh')
def login_refresh(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_refresh_token_required()
        current_user = Authorize.get_jwt_subject()

        access_token = Authorize.create_access_token(subject=str(current_user))

        return {
            'status': status.HTTP_201_CREATED,
            'access_token': access_token
        }

    except Exception as e:
        raise HTTPException(detail=f"{e}", status_code=status.HTTP_400_BAD_REQUEST)
