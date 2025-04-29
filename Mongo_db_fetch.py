from pymongo import MongoClient
import random
import ssl
# uri = "mongodb+srv://root123:root@cluster0/?tlsAllowInvalidCertificates=true"
uri = "mongodb+srv://root123:root@cluster0.jha4jws.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0&tlsAllowInvalidCertificates=true"

client = MongoClient(uri)
db = client["loandatabase"]
collection = db["loaninfo"]

# List of sample names
# names = [
#     "Alex", "Jamie", "Taylor", "Jordan", "Morgan", "Casey", "Drew", "Skyler",
#     "Riley", "Quinn", "Hayden", "Avery", "Reese", "Peyton", "Sawyer", "Cameron",
#     "Charlie", "Emerson", "Finley", "Rowan", "Harper", "Logan", "Dakota", "Blake",
#     "Phoenix", "River", "Sage", "Tatum", "Lennon", "Marley", "Elliot", "Jude",
#     "Kai", "Lane", "Parker", "Reagan", "Remy", "Shiloh", "Spencer", "Wren",
#     "Zion", "Arden", "Blaine", "Devon", "Hollis", "Jesse", "Kendall", "Micah", "Oakley", "Rory"
# ]
#
# # Generate 50 loan documents
# loan_documents = []
# for i in range(50):
#     loan_documents.append({
#         "customerName": names[i],
#         "loanAmount": random.randint(50000, 150000),
#         "interestRate": round(random.uniform(5.0, 10.0), 2),
#         "durationMonths": random.choice([12, 24, 36, 48])
#     })
#
# # Insert all documents
# collection.insert_many(loan_documents)
collection.insert_one({
    "customerName": "Adarsh",
    "loanAmount": 500000,
    "interestRate": 7.5,
    "durationMonths": 24
})


print("Inserted")

