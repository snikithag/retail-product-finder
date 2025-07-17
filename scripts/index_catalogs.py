import pandas as pd
import PyPDF2
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add project root to sys.path
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

from src.vector_db.chroma_db import ChromaDB

load_dotenv()

def extract_from_pdf(pdf_path: str) -> list:
    """Extract text from a PDF file and return a list of product dictionaries."""
    documents = []
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text = page.extract_text()
            lines = text.split("\n")
            current_category = None
            for line in lines:
                if line in ["Smartphones", "Laptops", "Tablets", "TVs", "Wearables", "Smart Home Devices", "Gaming Consoles", "Cameras", "Audio Devices"]:
                    current_category = line.lower()  # Normalize to lowercase
                elif line.startswith("- ") and current_category:
                    parts = line[2:].split(": ")
                    if len(parts) >= 2:
                        name_desc = parts[0]
                        details = parts[1].split(", Price: $")
                        if len(details) >= 2:
                            description = details[0]
                            price_stock = details[1].split(", ")
                            price = float(price_stock[0])
                            stock = price_stock[1]
                            brand = name_desc.split(" ")[0]
                            product_name = " ".join(name_desc.split(" ")[1:])
                            documents.append({
                                "category": current_category,
                                "brand": brand.lower(),
                                "product_name": product_name,
                                "description": description,
                                "price": price,
                                "stock": stock
                            })
    return documents

def index_catalogs():
    """Index all product catalogs in the data/catalogs directory."""
    chroma_db = ChromaDB()
    catalog_dir = "data/catalogs"
    
    # Process Excel files
    for file in os.listdir(catalog_dir):
        if file.endswith(".xlsx"):
            df = pd.read_excel(os.path.join(catalog_dir, file))
            # Normalize column names to lowercase
            df = df.rename(columns={
                "Category": "category",
                "Brand": "brand",
                "Product Name": "product_name",
                "Description": "description",
                "Price": "price",
                "Stock": "stock"
            })
            # Convert product_name to string to prevent integer issues
            df['product_name'] = df['product_name'].astype(str)
            documents = df.to_dict(orient="records")
            chroma_db.index_documents(documents)
    
    # Process PDF files
    for file in os.listdir(catalog_dir):
        if file.endswith(".pdf"):
            documents = extract_from_pdf(os.path.join(catalog_dir, file))
            chroma_db.index_documents(documents)

if __name__ == "__main__":
    index_catalogs()