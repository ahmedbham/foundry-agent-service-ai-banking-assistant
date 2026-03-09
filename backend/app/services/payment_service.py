import uuid

from ..models import PaymentRequest, PaymentResponse
from ..mock_data import ACCOUNTS


def submit_payment(request: PaymentRequest) -> PaymentResponse:
    if request.from_account_id not in ACCOUNTS:
        return PaymentResponse(
            payment_id="",
            status="failed",
            message=f"Account {request.from_account_id} not found.",
        )

    if request.amount <= 0:
        return PaymentResponse(
            payment_id="",
            status="failed",
            message="Payment amount must be greater than zero.",
        )

    payment_id = f"PAY-{uuid.uuid4().hex[:8].upper()}"
    return PaymentResponse(
        payment_id=payment_id,
        status="completed",
        message=f"Payment of ${request.amount:.2f} to {request.to_recipient} submitted successfully.",
    )
