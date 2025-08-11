import chromadb
from chromadb.utils import embedding_functions
from typing import List, Dict, Any
import os
from pathlib import Path

class ChromaDB:
    def __init__(self):
        chroma_path = os.path.join(Path(__file__).parent.parent.parent, "chroma_data")
        self.client = chromadb.PersistentClient(path=chroma_path)
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        self.collection = self.client.get_or_create_collection(
            name="products",
            embedding_function=self.embedding_function
        )

    def index_documents(self, documents: List[Dict[str, Any]]):
        """Index a list of product documents with dynamic schema."""
        for doc in documents:
            # Use dynamic keys; no hard-coded fields
            doc_id = str(hash(str(doc)))  # Unique ID from doc hash
            text = " ".join([f"{k}: {v}" for k, v in doc.items()])  # Concatenate all fields
            metadata = doc  # Store entire doc as metadata
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