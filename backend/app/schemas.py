from typing import Literal
from pydantic import BaseModel, ConfigDict, EmailStr, Field, AnyHttpUrl, field_validator

class StrictModel(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)

class Credentials(StrictModel):
    email: EmailStr
    password: str = Field(min_length=10, max_length=128)

class Registration(Credentials):
    fullName: str = Field(min_length=2, max_length=100)

class ResourceBody(StrictModel):
    title: str = Field(min_length=3, max_length=150)
    description: str = Field(default='', max_length=2000)
    url: AnyHttpUrl
    category: Literal['general', 'lecture', 'video', 'exercise'] = 'general'

    @field_validator('title')
    @classmethod
    def title_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError('Title cannot be blank')
        return value
