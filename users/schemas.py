from pydantic import BaseModel, Field
from typing import Optional


class SignUpSchema(BaseModel):
    first_name: Optional[str] = None
    username: str
    email: str
    password: str


    class Config:

        orm_mode = True
        schema_extra = {
                'example': {
                    'first_name': 'Alisherfayz',
                    'username': 'ehson',
                    'email': 'yana10kishigaehson@gmail.com',
                    'password': 'pass321'
                }
            }

class LoginSchema(BaseModel):
    username: str
    password: str


class Settings(BaseModel):
    authjwt_secret_key: str = "e6cb9b546658757296f08917c1c1effa96905dbc8a2fb626d02e511cc9b61303"