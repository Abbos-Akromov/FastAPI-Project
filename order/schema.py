from pydantic import BaseModel, Field
from typing import Optional


class CardItemSchema(BaseModel):
    quantity: int

class CardItemUpdateSchema(BaseModel):
    position: bool
