from ..mock_data import TRANSACTIONS


def search_transactions(query: str):
    query_lower = query.lower()
    return [
        t for t in TRANSACTIONS
        if query_lower in t.description.lower()
        or query_lower in t.category.lower()
        or query_lower in t.recipient.lower()
    ]


def get_transactions_by_recipient(recipient: str):
    recipient_lower = recipient.lower()
    return [
        t for t in TRANSACTIONS
        if recipient_lower in t.recipient.lower()
    ]
