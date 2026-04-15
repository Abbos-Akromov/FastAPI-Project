from users.models import User
from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from users.schemas import SignUpSchema, LoginSchema
from sqlalchemy.orm import Session
from database import engine, SessionLocal
from werkzeug.security import generate_password_hash, check_password_hash
from fastapi_jwt_auth import AuthJWT

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
    db_user = session.query(User).filter(User.username == data.username).first()

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

    access_token = Authorize.create_access_token(subject=str(db_user.id))
    refresh_token = Authorize.create_refresh_token(subject=str(db_user.id))

    return {
        'message': 'login',
        'access': access_token,
        'refresh': refresh_token
    }


