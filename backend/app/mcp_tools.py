from fastmcp import FastMCP

from .services import account_service, transaction_service, payment_service

mcp = FastMCP("Banking MCP Server")


@mcp.tool()
def get_account_info(account_id: str) -> dict:
    """Get banking account information for the given account ID."""
    account = account_service.get_account(account_id)
    if not account:
        return {"error": f"Account {account_id} not found."}
    return account.model_dump()


@mcp.tool()
def get_credit_balance(account_id: str) -> dict:
    """Get credit balance details for the given account ID, including available credit, current balance, and credit limit."""
    balance = account_service.get_balance(account_id)
    if not balance:
        return {"error": f"Balance for account {account_id} not found."}
    return balance.model_dump()


@mcp.tool()
def get_payment_methods(account_id: str) -> list[dict]:
    """Get registered payment methods for the given account ID."""
    methods = account_service.get_payment_methods(account_id)
    return [m.model_dump() for m in methods]


@mcp.tool()
def search_transactions(query: str) -> list[dict]:
    """Search transactions by keyword. Matches against description, category, or recipient."""
    results = transaction_service.search_transactions(query)
    return [t.model_dump(mode="json") for t in results]


@mcp.tool()
def get_transactions_by_recipient(recipient: str) -> list[dict]:
    """Get all transactions for a specific recipient."""
    results = transaction_service.get_transactions_by_recipient(recipient)
    return [t.model_dump(mode="json") for t in results]


@mcp.tool()
def submit_payment(from_account_id: str, to_recipient: str, amount: float, description: str = "") -> dict:
    """Submit a payment from an account to a recipient."""
    from .models import PaymentRequest

    request = PaymentRequest(
        from_account_id=from_account_id,
        to_recipient=to_recipient,
        amount=amount,
        description=description,
    )
    response = payment_service.submit_payment(request)
    return response.model_dump()
