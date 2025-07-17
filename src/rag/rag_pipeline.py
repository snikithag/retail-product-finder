from src.vector_db.chroma_db import ChromaDB

class RAGPipeline:
    def __init__(self):
        self.vector_db = ChromaDB()

    def get_context(self, query: str) -> str:
        """Retrieve relevant context from ChromaDB for the given query."""
        results = self.vector_db.search(query, k=5)
        context = "\n".join(
            f"{result['metadata']['product_name']}: {result['metadata']['description']}, Price: ${result['metadata']['price']}, {result['metadata']['stock']}"
            for result in results
        )
        return context if context else "No relevant products found in the local catalog."