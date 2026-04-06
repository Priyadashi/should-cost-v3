from pydantic import BaseModel
from typing import Optional


class PaginationParams(BaseModel):
    skip: int = 0
    limit: int = 50


class PaginatedResponse(BaseModel):
    items: list
    total: int
    skip: int
    limit: int
