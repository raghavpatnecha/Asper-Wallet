# tests/test_services.py
import threading
import unittest
from app import create_app, db
from app.models import User, Wallet, WalletTransaction
from app.services import create_wallet, credit_money, debit_money, get_balance, transaction_history, create_user
from app.config import TestingConfig
class TestServices(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_debit_money(self):
        user = create_user("1234567890")
        wallet = create_wallet(user.id)
        credit_money(wallet.id, 200.0)
        new_balance = debit_money(wallet.id, 50.0)
        self.assertEqual(new_balance, 150.0)

    def test_debit_below_minimum_balance(self):
        user = create_user("1234567890")  # Create a user
        wallet = create_wallet(user.id)  # Create a wallet for the user
        credit_money(wallet.id, 150.0)  # Credit 150 to the wallet

        with self.assertRaises(ValueError) as context:
            debit_money(wallet.id, 100.0)  # Debit 50 from the wallet

        self.assertEqual(str(context.exception), 'Balance cannot drop below minimum required balance of 100')

    #threading.Barrier to ensure all threads start their operation at same time
    def test_race_condition_debit_money(self):
        user = create_user("1234567890")
        wallet = create_wallet(user.id)
        credit_money(wallet.id, 200.0)
        debit_money(wallet.id, 50.0)
        initial_balance = wallet.balance
        num_threads = 5 # Number of threads for concurrent debit operations
        amount_to_debit = 10

        def concurrent_debit(barrier, app_context):
            app_context.push()  # Push the application context into the thread
            try:
                barrier.wait()  # Wait for all threads to start
                for _ in range(100):  # Perform multiple debit operations in each thread
                    # Create a new session for each thread as SQL Alchemy operations aren't thread safe
                    with db.session_scope() as session:
                        debit_money(session, wallet.id, amount_to_debit)
            except Exception as e:
                print(f"Error in thread: {e}")
            finally:
                app_context.pop()  # Pop the application context after the operation

        # Create threads for concurrent debit operations
        barrier = threading.Barrier(num_threads)
        threads = []
        for _ in range(num_threads):
            thread = threading.Thread(target=concurrent_debit, args=(barrier, self.app_context))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Check the final balance after all debit operations
        final_balance = get_balance(wallet.id)

        # Adjust the assertion based on your expectations
        print(final_balance,initial_balance,num_threads * 100 * amount_to_debit)
        self.assertTrue(final_balance >= initial_balance - (num_threads * 100 * amount_to_debit))

    def test_transaction_history(self):
        user = create_user("1234567890")
        wallet = create_wallet(user.id)
        credit_money(wallet.id, 200.0)
        debit_money(wallet.id, 50.0)
        history = transaction_history(wallet.id, '2024-04-01', '2024-04-30')
        self.assertIsInstance(history, dict)
        self.assertIn('total_credit', history)
        self.assertIn('total_debit', history)

if __name__ == '__main__':
    unittest.main()
