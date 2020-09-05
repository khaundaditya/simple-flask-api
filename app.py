from flask import Flask, jsonify
from flask import request
from flask import abort
from flask import make_response
from flask_ngrok import run_with_ngrok
from flask import Response
import json

app = Flask(__name__)
run_with_ngrok(app)  # Start ngrok when app is run

# Accounts data structure to be database table if persistence is desired
accounts = [
    {
        'id':'124',
        'balance':100,
    }
]

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
        account = _get_account_by_id(account_id)
        if len(account) == 0:
            val = '404 0'
            return Response('0', status=404, mimetype='application/json')
        #return(jsonify(200, account[0]['balance']))
        val = str(account[0]['balance'])
        return Response(str(account[0]['balance']), status=200, mimetype='application/json')


@app.route('/reset', methods=['POST'])
def reset():
    accounts = None
    return "OK"

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
            upd_acct = _update_account(account_id, amount,'deposit')
            s = '{ \"destination\" : ' +  upd_acct +'}'
            return Response(str(s), status=201, mimetype='application/json')
                        
            #return jsonify(({'destination': _update_account(account_id, amount, 'deposit') }))
        else:
            new_account = {
                'id':account_id,
                'balance':int(amount)
            }
            accounts.append(
                new_account
            )
            s = '{ \"destination\" : ' +  json.dumps(new_account,  separators=(",", ":")) +'}'
            val =  str(s)
            return Response(val, status=201, mimetype='application/json')
    elif action_type == 'withdraw':
        account_id = data['origin']
        amount  = data['amount']
        if not account_id or not amount:
            abort(404)
        account = _get_account_by_id(account_id)
        if len(account) > 0:
            data = _update_account(account_id, amount, 'withdraw')
            s = '{ \"origin\" : ' +  data +'}'
            return Response(str(s), status=201, mimetype='application/json')
        else:
            val = ' 0'
            return Response(val, status=404, mimetype='application/json')
    elif action_type == 'transfer':
        origin = data['origin']
        destination = data['destination']
        amount = data['amount']
        if not origin or not destination or not amount:
            abort(400)
        account = _get_account_by_id(origin)
        if len(account) > 0 :
           llist = _handle_money_transfer(origin, destination, amount)
           origin_json = json.dumps(llist[0], separators=(",", ":")),
           dest_json = json.dumps(llist[1], separators=(",", ":"))
           s =  '{ \"origin\" : ' +  str(origin_json[0]) + ', \"destination\": '+ str(dest_json) + '}'
           return Response(str(s), status=201, mimetype='application/json')

        else:
            val = ' 0'
            return Response(val, status=404, mimetype='application/json')

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
     account = [account for account in accounts if account['id'] == str(id)]
     return account

def _update_account(id, amount, action):
    account = _get_account_by_id(id)
    if action == 'deposit':
        cur_balance = account[0]['balance']
        account[0]['balance'] = cur_balance + int(amount)
        new = {
            'id':  account[0]['id'],
            'balance': account[0]['balance']
        }
        return json.dumps(new, separators=(",", ":"))
    elif action == 'withdraw':
        cur_balance = account[0]['balance']
        if cur_balance < amount:
            abort(500)
        else:
            account[0]['balance'] = cur_balance - int(amount)
            new = {
                'id':  account[0]['id'],
                'balance': account[0]['balance']
            }
            return json.dumps(new, separators=(",", ":"))

def _handle_money_transfer(origin, destination, amount):
    origin_account = _get_account_by_id(origin)
    origin_cur_balance = origin_account[0]['balance']
    # Check for sufficient balance in origin account
    if amount <= origin_cur_balance:
        origin_account[0]['balance'] = origin_cur_balance - amount
    else:
        abort(500)
    destination_account = _get_account_by_id(destination)
    if len(destination_account) <= 0:
        #destination account doesn't exist create it
        new_dest_account = {
            'id': destination,
            'balance': 0
        }
        accounts.append(new_dest_account)
    # fetch destination account again
    destination_account = _get_account_by_id(destination)
    destination_cur_balance = destination_account[0]['balance']
    destination_account[0]['balance'] = destination_cur_balance + amount
    orig_dict = {
        'id': origin_account[0]['id'],
        'balance': origin_account[0]['balance']
    }
    dest_dict = {
        'id': destination_account[0]['id'],
        'balance': destination_account[0]['balance']
    }
    return [orig_dict, dest_dict]



if __name__ == '__main__':
    app.run(debug=True)