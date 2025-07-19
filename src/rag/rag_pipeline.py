from src.vector_db.chroma_db import ChromaDB
from src.mcp_server.tools import search_online

class RAGPipeline:
    def __init__(self):
        self.db = ChromaDB()

    def retrieve(self, query: str) -> dict:
        local_results = self.db.search(query, k=5)
        online_results = search_online(query)
        
        context = {"local": [], "online": []}
        for result in local_results:
            metadata = result['metadata']
            context["local"].append({
                "product_name": metadata['product_name'],
                "Full Description": metadata['Full Description'],
                "price": metadata['price'],
                "stock": metadata['stock'],
                "brand": metadata['brand']
            })
        for result in online_results:
            context["online"].append({
                "title": result['title'],
                "price": result['price']
            })
        return context

if __name__ == "__main__":
    rag = RAGPipeline()
    query = "Phones with 128GB storage and 5G support"
    print(rag.retrieve(query))