from flask import Flask, jsonify
from flask import request
from flask import abort
from flask import make_response

app = Flask(__name__)

accounts = [
    {
        'id': '1234',
        'balance': 100,
    },
    {
        'id': '3456',
        'balance': 50
    }
]

"""

View Code 

""""

@app.route('/')
def index():
    return "Hello, World!"

@app.route('/ebanx/api/accounts', methods=['GET'])
def get_accounts():
    return jsonify({'accounts': accounts})


@app.route('/balance', methods=['GET'])
def get_balance():
    args = request.args
    if 'account_id' in args:
        account_id = args['account_id']
        print(account_id)
        account = _get_account_by_id(account_id)
        print(account)
        if len(account) == 0:
            abort(404)
        return jsonify(0), 200


@app.route('/event', methods=['POST'])
def post():
    if not request.json:
        abort(400)
    data = request.get_json()
    action_type = data['type']
    if action_type == 'deposit':
        account_id = data['destination']
        amount = data['amount']
        if not account_id or not amount:
            abort(400)
        account = _get_account_by_id(account_id)
        if ( len(account) > 0 ):
            # Deposit to existing account
            print("Reached Here")
            return jsonify(({'destination': _update_account(account_id, amount, 'deposit') }))
        else:
            new_account = {
                'id': account_id,
                'balance': int(amount)
            }
            accounts.append(
                new_account
            )
            return jsonify(201, ({'destination': new_account }))
    elif action_type == 'withdraw':
        account_id = data['destination']
        amount  = data['amount']
        if not account_id or not amount:
            abort(404)
        account = _get_account_by_id(account_id)
        if len(account) > 0:
            data = _update_account(account_id, amount, 'withdraw')
            return jsonify(201,({ 'destination': dict(destination) }))
        else:
            abort(404)
    elif action_type == 'transfer':
        origin = data['origin']
        destination = data['destination']
        amount = data['amount']
        if not origin or not destination or not amount:
            abort(400)
        account = _get_account_by_id(origin)
        if len(account) > 0 :
           origin, destination = _handle_money_transfer(origin, destination, amount)
           return jsonify(201,({'origin': dict(origin), 'destination': dict(destination) }))

        else:
            abort(404)

    return jsonify({'S': 'Failure'})

"""
Error Handlers
"""

@app.errorhandler(500)
def insufficient_funds(error):
    return make_response(jsonify({ 'error': 'Insufficient funds in your account'}, 500))

@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify( { 'error': 'Bad request' } ), 400)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify(404, 0 ))


"""
CRUD Functions 

"""

def _get_account_by_id(id):
     print(id)
     account = [account for account in accounts if account['id'] == str(id)]
     return account

def _update_account(id, amount, action):
    account = _get_account_by_id(id)
    if action == 'deposit':
        cur_balance = account[0]['balance']
        account[0]['balance'] = cur_balance + int(amount)
        return account[0]
    elif action == 'withdraw':
        cur_balance = account[0]['balance']
        if cur_balance < amount:
            abort(500)
        else:
            account[0]['balance'] = cur_balance - int(amount)
            return account[0]

def _handle_money_transfer(origin, destination, amount):
    origin_account = _get_account_by_id(origin)
    origin_cur_balance = origin_account[0]['balance']
    # Check for sufficient balance in origin account
    if origin_cur_balance < amount:
        abort(500)    
    else:
        origin_account[0]['balance'] = origin_cur_balance - amount
    destination_account = _get_account_by_id(destination)
    if ( len(destination_account) > 0 ):
        destination_cur_balance = destination_account[0]['balance']
        destination_account[0]['balance'] = destination_cur_balance + amount
        return ( origin_account[0], destination_account[0])
    else:
        abort(404)



if __name__ == '__main__':
    app.run(debug=True)