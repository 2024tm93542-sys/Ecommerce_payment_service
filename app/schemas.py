from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class PaymentCharge(BaseModel):
    order_id: int
    amount: float


class PaymentOut(BaseModel):
    payment_id: int
    order_id: int
    amount: float
    method: str
    status: bool
    reference: str
    created_at: datetime
    refunded: bool


class PaginatedPayments(BaseModel):
    items: List[PaymentOut]
    page: int
    per_page: int
    total: int


class RefundResponse(BaseModel):
    payment_id: int
    amount: float
    method: str
    message: str
