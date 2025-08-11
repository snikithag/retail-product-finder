import requests
from typing import List, Dict, Any
from src.vector_db.chroma_db import ChromaDB
from dotenv import load_dotenv
import os

load_dotenv()

def search_local_products(query: str, vector_db: ChromaDB) -> List[Dict[str, Any]]:
    """Search for products in the local ChromaDB catalog with dynamic schema."""
    results = vector_db.search(query, k=10)
    return [
        result["metadata"]  # Return full metadata as is
        for result in results
    ]

def search_online_products(query: str) -> List[Dict[str, Any]]:
    """Search for products online using SerpApi with dynamic schema."""
    serpapi_key = os.getenv("SERPAPI_KEY")
    if not serpapi_key:
        return []
    
    url = f"https://serpapi.com/search.json?engine=walmart&query={query}&api_key={serpapi_key}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        results = response.json().get("organic_results", [])
        return [
            item  # Return full item as dynamic dict
            for item in results[:10]
        ]
    except requests.RequestException:
        return []