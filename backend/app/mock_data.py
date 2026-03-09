from datetime import date
from .models import Account, CreditBalance, PaymentMethod, Transaction

ACCOUNTS = {
    "ACC001": Account(
        id="ACC001",
        name="John Smith",
        account_type="checking",
        account_number="****4521",
    ),
    "ACC002": Account(
        id="ACC002",
        name="John Smith",
        account_type="savings",
        account_number="****8734",
    ),
    "ACC003": Account(
        id="ACC003",
        name="John Smith",
        account_type="credit",
        account_number="****2190",
    ),
}

CREDIT_BALANCES = {
    "ACC001": CreditBalance(
        account_id="ACC001",
        available_credit=5200.00,
        current_balance=3480.75,
        credit_limit=10000.00,
    ),
    "ACC002": CreditBalance(
        account_id="ACC002",
        available_credit=15000.00,
        current_balance=12350.00,
        credit_limit=15000.00,
    ),
    "ACC003": CreditBalance(
        account_id="ACC003",
        available_credit=3200.00,
        current_balance=1800.50,
        credit_limit=5000.00,
    ),
}

PAYMENT_METHODS = {
    "ACC001": [
        PaymentMethod(id="PM001", account_id="ACC001", method_type="debit_card", last_four="4521", label="Primary Debit"),
        PaymentMethod(id="PM002", account_id="ACC001", method_type="bank_transfer", last_four="4521", label="ACH Transfer"),
    ],
    "ACC002": [
        PaymentMethod(id="PM003", account_id="ACC002", method_type="bank_transfer", last_four="8734", label="Savings Transfer"),
    ],
    "ACC003": [
        PaymentMethod(id="PM004", account_id="ACC003", method_type="credit_card", last_four="2190", label="Visa Credit Card"),
    ],
}

TRANSACTIONS = [
    Transaction(id="TXN001", account_id="ACC001", date=date(2026, 3, 1), description="Grocery shopping", amount=-85.50, recipient="Whole Foods", category="groceries"),
    Transaction(id="TXN002", account_id="ACC001", date=date(2026, 3, 2), description="Electric bill payment", amount=-120.00, recipient="City Power Co", category="utilities"),
    Transaction(id="TXN003", account_id="ACC001", date=date(2026, 3, 3), description="Salary deposit", amount=4500.00, recipient="Acme Corp", category="income"),
    Transaction(id="TXN004", account_id="ACC001", date=date(2026, 3, 4), description="Coffee shop", amount=-6.75, recipient="Starbucks", category="dining"),
    Transaction(id="TXN005", account_id="ACC001", date=date(2026, 3, 5), description="Transfer to Jane", amount=-200.00, recipient="Jane Doe", category="transfer"),
    Transaction(id="TXN006", account_id="ACC002", date=date(2026, 3, 1), description="Interest earned", amount=15.20, recipient="Bank", category="interest"),
    Transaction(id="TXN007", account_id="ACC002", date=date(2026, 3, 3), description="Transfer from checking", amount=500.00, recipient="John Smith", category="transfer"),
    Transaction(id="TXN008", account_id="ACC003", date=date(2026, 3, 2), description="Online purchase", amount=-45.99, recipient="Amazon", category="shopping"),
    Transaction(id="TXN009", account_id="ACC003", date=date(2026, 3, 4), description="Restaurant dinner", amount=-78.50, recipient="Olive Garden", category="dining"),
    Transaction(id="TXN010", account_id="ACC001", date=date(2026, 3, 6), description="Rent payment", amount=-1500.00, recipient="Jane Doe", category="housing"),
]
