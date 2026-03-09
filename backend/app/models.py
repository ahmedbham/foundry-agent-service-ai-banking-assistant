from pydantic import BaseModel
from typing import Optional
from datetime import date


class Account(BaseModel):
    id: str
    name: str
    account_type: str  # "checking", "savings", "credit"
    account_number: str


class CreditBalance(BaseModel):
    account_id: str
    available_credit: float
    current_balance: float
    credit_limit: float


class PaymentMethod(BaseModel):
    id: str
    account_id: str
    method_type: str  # "debit_card", "credit_card", "bank_transfer"
    last_four: str
    label: str


class Transaction(BaseModel):
    id: str
    account_id: str
    date: date
    description: str
    amount: float
    recipient: str
    category: str


class PaymentRequest(BaseModel):
    from_account_id: str
    to_recipient: str
    amount: float
    description: Optional[str] = None


class PaymentResponse(BaseModel):
    payment_id: str
    status: str
    message: str
