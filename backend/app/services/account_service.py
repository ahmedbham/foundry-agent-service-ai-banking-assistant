from ..mock_data import ACCOUNTS, CREDIT_BALANCES, PAYMENT_METHODS


def get_account(account_id: str):
    return ACCOUNTS.get(account_id)


def get_balance(account_id: str):
    return CREDIT_BALANCES.get(account_id)


def get_payment_methods(account_id: str):
    return PAYMENT_METHODS.get(account_id, [])
