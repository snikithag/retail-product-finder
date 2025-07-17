import os
import requests
from dotenv import load_dotenv
from groq import Groq
from src.vector_db.chroma_db import ChromaDB

load_dotenv()

class Chatbot:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.vector_db = ChromaDB()
        self.serpapi_key = os.getenv("SERPAPI_KEY")
        if not self.serpapi_key:
            print("Warning: SERPAPI_KEY not found in .env file. Online search disabled.")
        self.model = "llama-3.3-70b-versatile"

    def _serpapi_search(self, query: str, num_results: int = 5) -> list:
        """Search for products using SerpApi."""
        if not self.serpapi_key:
            return []
        try:
            params = {
                "q": query,
                "tbm": "shop",
                "api_key": self.serpapi_key,
                "num": num_results
            }
            response = requests.get("https://serpapi.com/search", params=params)
            response.raise_for_status()
            results = response.json().get("shopping_results", [])
            return [
                {
                    "title": result.get("title", ""),
                    "snippet": result.get("snippet", ""),
                    "price": result.get("price", "N/A"),
                    "link": result.get("link", "")
                }
                for result in results
            ]
        except requests.RequestException as e:
            print(f"Error during SerpApi search: {e}")
            return []

    def generate_response(self, query: str) -> str:
        """Generate a response for the user's query."""
        # Search local catalog
        local_results = self.vector_db.search(query, k=5)
        local_products = [
            f"- {result['metadata']['product_name']}: {result['metadata']['description']}, "
            f"Price: ${result['metadata']['price']}, {result['metadata']['stock']}"
            for result in local_results
        ]
        local_response = (
            "Based on the local catalog:\n" + "\n".join(local_products)
            if local_products
            else "No matching products found in the local catalog."
        )

        # Fallback to SerpApi if no local results
        if not local_products and self.serpapi_key:
            serp_results = self._serpapi_search(query)
            if serp_results:
                local_response += "\n\nOnline results:\n" + "\n".join(
                    f"- {result['title']}: {result.get('snippet', '')}, Price: {result.get('price', 'N/A')}"
                    for result in serp_results
                )
            else:
                local_response += "\n\nNo online results found."

        # Generate response using Groq
        prompt = (
            f"You are a retail assistant. The user asked: '{query}'. "
            f"Here are the search results:\n{local_response}\n\n"
            f"Provide a concise, helpful response summarizing the results."
        )
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful retail assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content

    def run(self):
        """Run the chatbot interactively."""
        print("Welcome to the VoltEdge Retail Chatbot! Type 'exit' to quit.")
        while True:
            query = input("Enter your query (e.g., 'Phones with 128GB storage and 5G support'): ")
            if query.lower() == "exit":
                break
            response = self.generate_response(query)
            print(response)

if __name__ == "__main__":
    chatbot = Chatbot()
    chatbot.run()