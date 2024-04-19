import time
from app.models import db, Wallet, User, WalletTransaction
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm.exc import StaleDataError


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

def credit_money(wallet_id, amount, minimum_balance=100):
    try:
        wallet = Wallet.query.get(wallet_id)
        if not wallet:
            raise ValueError("Wallet not found")

        if wallet.balance + amount < minimum_balance:
            raise ValueError(f'You need to add minimum {minimum_balance} in your wallet')

        # Update wallet balance
        wallet.balance += amount
        wallet.version += 1  # Increment version for optimistic locking

        # Create transaction record
        transaction = WalletTransaction(wallet_id=wallet_id, amount=amount, type='credit')
        db.session.add(transaction)
        db.session.commit()

        return wallet.balance
    except IntegrityError as e:
        db.session.rollback()
        raise ValueError("Database integrity error: Unable to credit money")
    except Exception as e:
        db.session.rollback()
        raise ValueError(f"Database error: Unable to credit money: {str(e)}")




def debit_money(wallet_id, amount, minimum_balance=100,retries=3, delay=1):
    """
        Attempts to debit an amount from a wallet.
        Ensures the balance does not fall below a specified minimum after the transaction.

        :param wallet_id: ID of the wallet to debit from.
        :param amount: Amount to debit.
        :param minimum_balance: Minimum allowable balance after debit.
        :return: New balance if successful.
        :raises ValueError: If balance is insufficient or wallet does not exist.
        #To Prevent the Race conditions following logic is implemented

        1.Lock the wallet record during this transaction to prevent race conditions.
         with_for_update() effectively locks the row in the database,
         which prevents other transactions from accessing the wallet while it's being updated,

        2. Optimistic Locking: The function now assumes that the Wallet model has a version column
        that is incremented each time the wallet is updated.
        This version number is used to detect conflicts at commit time.
        If a StaleDataError is caught, it indicates a conflict, and the transaction is retried after a delay.

        3.Retry Logic: The function includes a retry mechanism that attempts to debit the wallet up to a specified
         number of times (retries) with a delay (delay) between attempts.
         This is useful for handling temporary conflicts or database issues that might resolve themselves after a short wait.

        4.Error Handling: The function now specifically catches StaleDataError to handle conflicts detected
        by optimistic locking. It also includes a generic SQLAlchemyError catch for other database errors.
        """
    for attempt in range(retries):
        try:
            with db.session.begin_nested():
                wallet = Wallet.query.filter_by(id=wallet_id).with_for_update().first()
                if not wallet:
                    raise ValueError("Wallet not found")

                if wallet.balance < amount:
                    raise ValueError('Insufficient balance')

                if wallet.balance - amount < minimum_balance:
                    raise ValueError(f'Balance cannot drop below minimum required balance of {minimum_balance}')

                wallet.balance -= amount  # Update balance

                # Create transaction record
                transaction = WalletTransaction(wallet_id=wallet_id, amount=amount, type='debit')
                db.session.add(transaction)

            # Commit transaction
            db.session.commit()
            return wallet.balance
        except StaleDataError:
            # Handle StaleDataError due to optimistic locking conflict
            db.session.rollback()
            if attempt < retries - 1:  # Don't sleep on the last attempt
                time.sleep(delay)
            else:
                raise ValueError("Transaction conflict detected. Please retry the transaction.")
        except IntegrityError as e:
            db.session.rollback()
            raise ValueError("Database integrity error: Unable to debit money")
        except SQLAlchemyError as e:
            db.session.rollback()
            raise ValueError(f"Database error: Unable to debit money:{str(e)}")


def get_balance(wallet_id):
    wallet = Wallet.query.get(wallet_id)
    if not wallet:
        raise ValueError("Wallet not found")
    return wallet.balance


def transaction_history(wallet_id, start_date, end_date):
    wallet = Wallet.query.get(wallet_id)
    if not wallet:
        raise ValueError("Wallet not found")

    transactions = WalletTransaction.query \
        .filter(WalletTransaction.wallet_id == wallet_id) \
        .filter(WalletTransaction.timestamp.between(start_date, end_date)) \
        .all()

    #commenting transaction history and adding logic for total credit and debit as per assignment
    #return [{'amount': txn.amount, 'type': txn.type, 'date': txn.timestamp} for txn in transactions]
    # Initialize total amounts
    total_credit = 0
    total_debit = 0

    transaction_list = []
    for txn in transactions:
        amount = txn.amount
        txn_type = txn.type
        date = txn.timestamp

        # Update total amounts based on transaction type
        if txn_type == 'credit':
            total_credit += amount
        elif txn_type == 'debit':
            total_debit += amount

        # Append transaction details to the list
        transaction_list.append({'amount': amount, 'type': txn_type, 'date': date})

    # Create response dictionary with transaction history and total amounts
    response = {
        'total_credit': total_credit,
        'total_debit': total_debit,
        'history': transaction_list
    }

    return response

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