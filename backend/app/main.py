from typing import Optional

from fastapi import FastAPI, HTTPException, Query

from .models import PaymentRequest
from .services import account_service, transaction_service, payment_service
from .mcp_tools import mcp


mcp_app = mcp.http_app(transport="streamable-http")

app = FastAPI(title="Banking Backend API", version="1.0.0", lifespan=mcp_app.lifespan)

# Mount FastMCP as an ASGI sub-application at /mcp
app.mount("/mcp", mcp_app)


# ── Account Endpoints ──────────────────────────────────────────────

@app.get("/accounts/{account_id}")
def get_account(account_id: str):
    account = account_service.get_account(account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


@app.get("/accounts/{account_id}/balance")
def get_balance(account_id: str):
    balance = account_service.get_balance(account_id)
    if not balance:
        raise HTTPException(status_code=404, detail="Balance not found")
    return balance


@app.get("/accounts/{account_id}/payment-methods")
def get_payment_methods(account_id: str):
    return account_service.get_payment_methods(account_id)


# ── Transaction Endpoints ──────────────────────────────────────────

@app.get("/transactions")
def get_transactions(
    query: Optional[str] = Query(None, description="Search keyword"),
    recipient: Optional[str] = Query(None, description="Filter by recipient"),
):
    if recipient:
        return transaction_service.get_transactions_by_recipient(recipient)
    if query:
        return transaction_service.search_transactions(query)
    return transaction_service.search_transactions("")


# ── Payment Endpoints ──────────────────────────────────────────────

@app.post("/payments")
def make_payment(request: PaymentRequest):
    response = payment_service.submit_payment(request)
    if response.status == "failed":
        raise HTTPException(status_code=400, detail=response.message)
    return response


@app.get("/health")
def health():
    return {"status": "healthy"}
