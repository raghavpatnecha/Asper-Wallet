from app.models import db, Wallet, User
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime


def create_wallet(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            raise ValueError("User does not exist")

        existing_wallet = Wallet.query.filter_by(user_id=user_id).first()
        if existing_wallet:
            # If the user already has a wallet, return the wallet ID
            raise ValueError("User already has a wallet with id:"+str(existing_wallet.id))

        new_wallet = Wallet(user_id=user_id, balance=0.0)
        db.session.add(new_wallet)
        db.session.commit()
        return new_wallet
    except SQLAlchemyError as e:
        db.session.rollback()
        raise ValueError("Database error: Unable to create wallet")


def credit_money(wallet_id, amount):
    try:
        wallet = Wallet.query.get(wallet_id)
        if not wallet:
            raise ValueError("Wallet not found")

        wallet.balance += amount
        db.session.commit()
        return wallet.balance
    except SQLAlchemyError as e:
        db.session.rollback()
        raise ValueError("Database error: Unable to credit money")


def debit_money(wallet_id, amount, minimum_balance):
    """
        Attempts to debit an amount from a wallet.
        Ensures the balance does not fall below a specified minimum after the transaction.

        :param wallet_id: ID of the wallet to debit from.
        :param amount: Amount to debit.
        :param minimum_balance: Minimum allowable balance after debit.
        :return: New balance if successful.
        :raises ValueError: If balance is insufficient or wallet does not exist.
        """
    try:
        wallet = Wallet.query.get(wallet_id)
        if not wallet:
            raise ValueError("Wallet not found")

        if wallet.balance - amount < minimum_balance:
            raise ValueError(f'Balance cannot drop below minimum required balance of {minimum_balance}')


        wallet.balance -= amount
        db.session.commit()
        return wallet.balance
    except SQLAlchemyError as e:
        db.session.rollback()
        raise ValueError("Database error: Unable to debit money")


def get_balance(wallet_id):
    wallet = Wallet.query.get(wallet_id)
    if not wallet:
        raise ValueError("Wallet not found")
    return wallet.balance


def transaction_history(wallet_id, start_date, end_date):
    wallet = Wallet.query.get(wallet_id)
    if not wallet:
        raise ValueError("Wallet not found")

    transactions = wallet.transactions.filter(
        WalletTransaction.timestamp.between(start_date, end_date)
    ).all()
    return [{'amount': txn.amount, 'type': txn.type, 'date': txn.timestamp} for txn in transactions]

def create_user(phone_number):
    # Check if the user already exists
    existing_user = User.query.filter_by(phone_number=phone_number).first()
    if existing_user:
        raise ValueError("User already exists")

    # Create a new user
    new_user = User(phone_number=phone_number)

    # Add the new user to the database session
    db.session.add(new_user)

    try:
        # Commit the changes to the database
        db.session.commit()
        return new_user
    except Exception as e:
        # Rollback changes if an error occurs
        db.session.rollback()
        raise ValueError("Failed to create user")