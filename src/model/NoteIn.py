from uuid import uuid1
from pydantic import BaseModel, Extra
from typing import Union
from datetime import date

class NoteIn(BaseModel):
    title: Union[str, None] = None
    content: Union[str, None] = None
    autor: Union[str, None] = None

    class Config:
        extra = Extra.allow


