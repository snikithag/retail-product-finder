from typing import List, Dict, Any
from src.vector_db.chroma_db import ChromaDB
from src.mcp_server.tools import search_local_products, search_online_products

class MCPServer:
    def __init__(self):
        self.vector_db = ChromaDB()

    def search(self, query: str, use_online: bool = False) -> List[Dict[str, Any]]:
        # Prioritize local catalog search
        results = search_local_products(query, self.vector_db)
        
        # Fallback to online search if requested and no local results
        if use_online and not results:
            results = search_online_products(query)
        
        return results

    def get_product_details(self, product_id: str) -> Dict[str, Any]:
        # Retrieve specific product details from ChromaDB
        return self.vector_db.get_product_by_id(product_id)