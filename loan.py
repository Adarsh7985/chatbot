from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson import ObjectId
import json

app = Flask(__name__)

# Connect to MongoDB
uri = "mongodb+srv://root123:root@cluster0.jha4jws.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0&tlsAllowInvalidCertificates=true"

client = MongoClient(uri)
db = client["loandatabase"]
collection = db["loaninfo"]

# Helper to convert ObjectId to string
class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

@app.route('/loans', methods=['POST'])
def add_loan():
    data = request.json
    result = collection.insert_one(data)
    return jsonify({"message": "Loan added", "id": str(result.inserted_id)}), 201

@app.route('/loans', methods=['GET'])
def get_loans():
    print("route working")
    loans = list(collection.find())
    return JSONEncoder().encode(loans)

@app.route('/loans/<name>', methods=['GET'])
def get_loan_by_name(name):
    loan = collection.find_one({"customerName": name})
    if loan:
        return JSONEncoder().encode(loan)
    return jsonify({"error": "Loan not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
