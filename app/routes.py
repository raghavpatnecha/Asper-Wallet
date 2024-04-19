from flask import Blueprint, request, jsonify
from .services import create_wallet, credit_money, debit_money, get_balance, transaction_history,create_user

# Create a Blueprint for better organization
wallet_bp = Blueprint('wallet', __name__)


@wallet_bp.route('/wallet/create', methods=['POST'])
def api_create_wallet():
    user_id = request.json.get('user_id')
    if not user_id:
        return jsonify(error="User ID is required"), 400
    try:
        wallet = create_wallet(user_id)
        return jsonify(wallet_id=wallet.id), 201
    except ValueError as e:
        return jsonify(error=str(e)), 400

@wallet_bp.route('/wallet/credit', methods=['POST'])
def api_credit_money():
    wallet_id = request.json.get('wallet_id')
    amount = request.json.get('amount')
    if not all([wallet_id, amount]):
        return jsonify(error="Wallet ID and amount are required"), 400
    try:
        new_balance = credit_money(wallet_id, amount)
        return jsonify(new_balance=new_balance), 200
    except ValueError as e:
        return jsonify(error=str(e)), 400

@wallet_bp.route('/wallet/debit', methods=['POST'])
def api_debit_money():
    wallet_id = request.json.get('wallet_id')
    amount = request.json.get('amount')
    minimum_balance = request.json.get('minimum_balance', 0)  # Optional minimum balance from request
    if not all([wallet_id, amount]):
        return jsonify(error="Wallet ID and amount are required"), 400
    try:
        new_balance = debit_money(wallet_id, amount, minimum_balance)
        return jsonify(new_balance=new_balance), 200
    except ValueError as e:
        return jsonify(error=str(e)), 400

@wallet_bp.route('/wallet/balance/<int:wallet_id>', methods=['GET'])
def api_get_balance(wallet_id):
    try:
        balance = get_balance(wallet_id)
        return jsonify(balance=balance), 200
    except ValueError as e:
        return jsonify(error=str(e)), 400

@wallet_bp.route('/wallet/transactions', methods=['GET'])
def api_transaction_history():
    wallet_id = request.args.get('wallet_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    if not wallet_id:
        return jsonify(error="Wallet ID is required"), 400
    try:
        history = transaction_history(wallet_id, start_date, end_date)
        return jsonify(history=history), 200
    except ValueError as e:
        return jsonify(error=str(e)), 400

@wallet_bp.route('/register', methods=['POST'])
def register_user():
    phone_number = request.json.get('phone_number')

    # Check if the phone number is provided
    if not phone_number:
        return jsonify(error="Phone number is required"), 400

    try:
        # Create the user
        new_user = create_user(phone_number)
        return jsonify(message="User created successfully", user_id=new_user.id), 201
    except ValueError as e:
        return jsonify(error=str(e)), 400

def init_app(app):
    app.register_blueprint(wallet_bp)
