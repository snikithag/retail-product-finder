import os
import pandas as pd
import PyPDF2
from pathlib import Path
import sys
from dotenv import load_dotenv
from groq import Groq

# Add project root to sys.path
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

from src.vector_db.chroma_db import ChromaDB

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def infer_schema_and_parse(text: str) -> list:
    """Use Groq to infer schema and parse text into structured documents."""
    prompt = f"""
    You are a data extraction AI. Given the following document text, infer the schema (e.g., fields like category, brand, product_name, description, price, stock) and parse it into a list of product dictionaries. Be dynamic and don't assume fixed fields; detect what makes sense from the content. For example, if it's a catalog, extract product names, descriptions, prices, etc.
    Document text: {text}
    Return a list of dictionaries, e.g., [{'category': 'smartphones', 'brand': 'samsung', 'product_name': 'Galaxy S24', 'description': '128GB Storage...', 'price': 699, 'stock': 'In Stock'}]
    """
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=2000
    )
    parsed_response = eval(response.choices[0].message.content)  # Dangerous eval, use json in production
    return parsed_response

def extract_from_pdf(pdf_path: str) -> str:
    """Extract text from PDF."""
    text = ""
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text

def index_catalogs():
    """Dynamically index catalogs using Groq to infer schema."""
    chroma_db = ChromaDB()
    catalog_dir = "data/catalogs"
    
    documents = []
    for file in os.listdir(catalog_dir):
        file_path = os.path.join(catalog_dir, file)
        if file.endswith(".xlsx"):
            df = pd.read_excel(file_path)
            text = df.to_string()
            parsed_documents = infer_schema_and_parse(text)
            documents.extend(parsed_documents)
        elif file.endswith(".pdf"):
            text = extract_from_pdf(file_path)
            parsed_documents = infer_schema_and_parse(text)
            documents.extend(parsed_documents)
    
    if documents:
        chroma_db.index_documents(documents)

if __name__ == "__main__":
    index_catalogs()