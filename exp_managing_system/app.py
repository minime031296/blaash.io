from flask import Flask, request, jsonify
from flask_pymongo import PyMongo

app = Flask(__name__)

app.config['MONGO_URI'] = 'mongodb://127.0.0.1:27017/expense_management'
mongo = PyMongo(app)

@app.route('/', methods=["GET"])
def HomePage():
    return jsonify({"message":"WELCOME TO BANKING SYSTEM"})

@app.route('/api/users/<user_id>/accounts/<account_id>/expenses', methods=['POST'])
def post_user_expenses_details(user_id, account_id):
    data = request.json
    expenses_collection = mongo.db.expenses
    result = expenses_collection.insert_one(data)
    return jsonify({'result': 'success', 'id': str(result.inserted_id)})

@app.route('/api/users/<user_id>/accounts/<account_id>/expenses', methods=['GET'])
def get_user_expenses_details(user_id, account_id):
    expenses_collection = mongo.db.expenses
    expenses = expenses_collection.find({'user_id': user_id, 'account_id': account_id})
    expense_list = list(expenses)
    for expense in expense_list:
        expense['_id'] = str(expense['_id'])  
    return jsonify(expense_list)

if __name__ == '__main__':
    app.run(port=5000)
