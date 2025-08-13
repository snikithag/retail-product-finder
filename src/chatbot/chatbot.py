import os
from groq import Groq
from src.vector_db.chroma_db import ChromaDB
from src.mcp_server.tools import search_local_products, search_online_products
from dotenv import load_dotenv

load_dotenv()

class Chatbot:
    def __init__(self):
        self.db = ChromaDB()
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama-3.3-70b-versatile"

    def process_query(self, query: str) -> str:
        # Search local catalog
        local_results = self.db.search(query, k=5)
        response = "Response: Based on the local catalog:\n"
        if local_results:
            for result in local_results:
                metadata = result['metadata']
                brand = metadata.get('brand', 'Unknown Brand')
                product_name = metadata.get('product_name', 'Unknown Product')
                description = metadata.get('description', metadata.get('Full Description', 'No description available'))
                price = metadata.get('price', 'N/A')
                stock = metadata.get('stock', 'Stock unknown')
                
                response += f"- {brand} {product_name}: {description}, Price: ${price}, {stock}\n"
        else:
            response += "Unfortunately, we don't have any matching products in our local catalog.\n"

        # Fallback to online search
        response += "Online results:\n"
        online_results = search_online_products(query)
        if online_results:
            for result in online_results:
                response += f"- {result.get('product_name', 'Unknown Product')}: ${result.get('price', 'N/A')}\n"
        else:
            response += "No online results found.\n"

        # Generate response with Groq
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a retail assistant. Provide a concise, helpful response based on the search results."},
                {"role": "user", "content": f"Query: {query}\nResults:\n{response}"}
            ]
        )
        return completion.choices[0].message.content

if __name__ == "__main__":
    chatbot = Chatbot()
    while True:
        query = input("Enter your query (e.g., 'Phones with 128GB storage and 5G support'): ")
        if query.lower() == "exit":
            break
        print(chatbot.process_query(query))