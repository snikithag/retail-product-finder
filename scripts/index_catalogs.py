import os
import pandas as pd
import PyPDF2
from pathlib import Path
import sys
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
            if not text:
                continue
            lines = text.split("\n")
            current_category = None
            for line in lines:
                if line in ["Smartphones", "Laptops", "Tablets", "TVs", "Wearables", "Smart Home Devices", "Gaming Consoles", "Cameras", "Audio Devices"]:
                    current_category = line.lower()
                elif line.startswith("- ") and current_category:
                    parts = line[2:].split(": ")
                    if len(parts) >= 2:
                        name_desc = parts[0]
                        details = parts[1].split(", Price: $")
                        if len(details) >= 2:
                            full_description = details[0].strip()
                            price_stock = details[1].split(", ")
                            price = float(price_stock[0])
                            stock = price_stock[1].strip()
                            brand = name_desc.split(" ")[0]
                            product_name = " ".join(name_desc.split(" ")[1:])
                            documents.append({
                                "category": current_category,
                                "brand": brand.lower(),
                                "product_name": product_name,
                                "Full Description": full_description,
                                "price": price,
                                "stock": stock
                            })
    return documents

def index_catalogs():
    """Index all product catalogs in the data/catalogs directory."""
    chroma_db = ChromaDB()
    catalog_dir = "data/catalogs"
    
    # Process Excel files
    excel_documents = []
    for file in os.listdir(catalog_dir):
        if file.endswith(".xlsx"):
            df = pd.read_excel(os.path.join(catalog_dir, file))
            df = df.rename(columns={
                "Category": "category",
                "Brand": "brand",
                "Product Name": "product_name",
                "Full Description": "Full Description",
                "Price": "price",
                "Stock": "stock"
            })
            df['product_name'] = df['product_name'].astype(str)
            excel_documents.extend(df.to_dict(orient="records"))
    
    if excel_documents:
        chroma_db.index_documents(excel_documents)
    
    # Process PDF files
    pdf_documents = []
    for file in os.listdir(catalog_dir):
        if file.endswith(".pdf"):
            pdf_documents.extend(extract_from_pdf(os.path.join(catalog_dir, file)))
    
    if pdf_documents:
        chroma_db.index_documents(pdf_documents)

if __name__ == "__main__":
    index_catalogs()