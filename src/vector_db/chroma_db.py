import chromadb
from chromadb.utils import embedding_functions
from typing import List, Dict, Any
import os
from pathlib import Path

class ChromaDB:
    def __init__(self):
        # Use PersistentClient with explicit path
        chroma_path = os.path.join(Path(__file__).parent.parent.parent, "chroma_data")
        self.client = chromadb.PersistentClient(path=chroma_path)
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        self.collection = self.client.get_or_create_collection(
            name="products",
            embedding_function=self.embedding_function
        )

    def index_documents(self, documents: List[Dict[str, Any]]):
        """Index a list of product documents into ChromaDB."""
        for doc in documents:
            category = doc.get('category', 'unknown')
            product_name = str(doc.get('product_name', 'unknown_product'))
            full_description = doc.get('Full Description', '')
            price = doc.get('price', 0.0)
            stock = doc.get('stock', 'Unknown')
            
            doc_id = f"{category}_{product_name.replace(' ', '_')}"
            text = f"{product_name}: {full_description}, Price: ${price}, {stock}"
            metadata = {
                "category": category,
                "brand": doc.get('brand', 'unknown'),
                "product_name": product_name,
                "Full Description": full_description,
                "price": price,
                "stock": stock
            }
            self.collection.add(
                ids=[doc_id],
                documents=[text],
                metadatas=[metadata]
            )

    def search(self, query: str, k: int = 10) -> List[Dict[str, Any]]:
        """Search for products in ChromaDB based on the query."""
        results = self.collection.query(query_texts=[query], n_results=k)
        return [
            {"id": id, "metadata": metadata}
            for id, metadata in zip(results["ids"][0], results["metadatas"][0])
        ]

    def get_product_by_id(self, product_id: str) -> Dict[str, Any]:
        """Retrieve a product by its ID."""
        results = self.collection.get(ids=[product_id])
        return results["metadatas"][0] if results["metadatas"] else {}