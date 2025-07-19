import requests
from typing import List, Dict, Any
from src.vector_db.chroma_db import ChromaDB
from dotenv import load_dotenv
import os

load_dotenv()

def search_local_products(query: str, vector_db: ChromaDB) -> List[Dict[str, Any]]:
    """Search for products in the local ChromaDB catalog."""
    results = vector_db.search(query, k=10)
    return [
        {
            "product_name": result["metadata"]["product_name"],
            "Full Description": result["metadata"]["Full Description"],
            "price": result["metadata"]["price"],
            "stock": result["metadata"]["stock"],
            "category": result["metadata"]["category"],
            "brand": result["metadata"]["brand"]
        }
        for result in results
    ]

def search_online_products(query: str) -> List[Dict[str, Any]]:
    """Search for products online using SerpApi."""
    serpapi_key = os.getenv("SERPAPI_KEY")
    if not serpapi_key:
        return []
    
    url = f"https://serpapi.com/search.json?engine=walmart&query={query}&api_key={serpapi_key}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        results = response.json().get("organic_results", [])
        return [
            {
                "product_name": item["title"],
                "Full Description": item.get("description", ""),
                "price": item["primary_offer"]["offer_price"],
                "stock": "In Stock" if item.get("quantity", 0) > 0 else "Out of Stock",
                "category": item.get("category", "Unknown"),
                "brand": item.get("brand", "Unknown")
            }
            for item in results[:10]
        ]
    except requests.RequestException:
        return []