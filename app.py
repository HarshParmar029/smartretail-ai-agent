from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
client_mongo = MongoClient(os.getenv("MONGODB_URI"))
db = client_mongo["sample_supplies"]

def get_retail_data(query):
    collection = db["sales"]
    locations = collection.distinct("storeLocation")
    samples = list(collection.find({}, {"_id": 0, "items": 1, "storeLocation": 1}).limit(5))
    
    response = f"🏪 Store Locations: {', '.join(locations)}\n\n📦 Sample Products:\n"
    for s in samples[:3]:
        loc = s.get('storeLocation', '')
        if 'items' in s:
            for item in s['items'][:2]:
                name = item.get('name', 'Product')
                price = item.get('price', 'N/A')
                response += f"• {name} - ${price} @ {loc}\n"
    return response

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    query = data.get("query", "")
    if not query:
        return jsonify({"error": "No query provided"}), 400
    try:
        response = get_retail_data(query)
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/health")
def health():
    return jsonify({"status": "OK"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)