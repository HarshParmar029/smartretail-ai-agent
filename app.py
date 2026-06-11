from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
client_mongo = MongoClient(os.getenv("MONGODB_URI"))
db = client_mongo["sample_mflix"]

def get_retail_data(query):
    try:
        collection = db["movies"]
        q = query.lower()
        
        if "location" in q or "store" in q:
            sample = list(collection.distinct("countries"))[:8]
            return "🏪 Available Locations (from MongoDB Atlas):\n\n" + ", ".join(sample)
        
        elif "best" in q or "selling" in q or "popular" in q:
            sample = list(collection.find({"imdb.rating": {"$gt": 8}}, {"_id": 0, "title": 1, "imdb": 1}).sort("imdb.rating", -1).limit(5))
            response = "🛍️ Top Rated Products (live from MongoDB):\n\n"
            for item in sample:
                rating = item.get('imdb', {}).get('rating', 'N/A')
                response += f"• {item.get('title','')} — Rating: {rating}\n"
            return response
        
        else:
            # Try searching by title keyword
            search_results = list(collection.find(
                {"title": {"$regex": query, "$options": "i"}},
                {"_id": 0, "title": 1, "year": 1, "genres": 1}
            ).limit(5))
            
            if search_results:
                response = f"🔍 Search results for '{query}':\n\n"
                for item in search_results:
                    response += f"• {item.get('title','')} ({item.get('year','')}) - {', '.join(item.get('genres', []))}\n"
                return response
            
            sample = list(collection.find({}, {"_id": 0, "title": 1, "year": 1, "genres": 1}).limit(5))
            if not sample:
                return "No data found in MongoDB"
            response = "📦 Sample Inventory (live from MongoDB Atlas):\n\n"
            for item in sample:
                response += f"• {item.get('title','')} ({item.get('year','')}) - {', '.join(item.get('genres', []))}\n"
            return response
    except Exception as e:
        return f"DB Error: {str(e)}"

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