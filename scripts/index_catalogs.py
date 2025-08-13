import os
import pandas as pd
import PyPDF2
from pathlib import Path
import sys
import json
import re
from dotenv import load_dotenv
from groq import Groq

# Add project root to sys.path
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

from src.vector_db.chroma_db import ChromaDB

load_dotenv()

# Check if GROQ_API_KEY is set
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    print("ERROR: GROQ_API_KEY environment variable is not set!")
    print("Please set the GROQ_API_KEY environment variable to index catalogs.")
    print("You can create a .env file in the project root with:")
    print("GROQ_API_KEY=your_actual_api_key_here")
    sys.exit(1)

print(f"GROQ_API_KEY found: {groq_api_key[:10]}...")

client = Groq(api_key=groq_api_key)

def clean_and_parse_response(response_text: str) -> list:
    """Clean and safely parse the LLM response."""
    try:
        # Try to extract JSON-like content
        # Look for content between square brackets
        match = re.search(r'\[.*\]', response_text, re.DOTALL)
        if match:
            json_str = match.group(0)
            # Replace single quotes with double quotes for JSON parsing
            json_str = json_str.replace("'", '"')
            # Try to parse as JSON
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass
        
        # Fallback: try to evaluate as Python literal
        # Remove any markdown formatting
        cleaned = re.sub(r'```python\s*|\s*```', '', response_text)
        cleaned = cleaned.strip()
        
        # Try to find the actual list content
        if cleaned.startswith('[') and cleaned.endswith(']'):
            return eval(cleaned)
        
        print(f"Could not parse response: {response_text[:200]}...")
        return []
        
    except Exception as e:
        print(f"Error parsing response: {e}")
        print(f"Response text: {response_text[:200]}...")
        return []

def infer_schema_and_parse(text: str) -> list:
    """Use Groq to infer schema and parse text into structured documents."""
    try:
        prompt = """You are a data extraction AI. Given the following document text, extract product information and return it as a valid Python list of dictionaries.

Document text: {text}

Extract products and return ONLY a valid Python list like this example:
[
    {{"category": "smartphones", "brand": "Samsung", "product_name": "Galaxy S24", "description": "128GB Storage", "price": 699, "stock": "In Stock"}},
    {{"category": "laptops", "brand": "Dell", "product_name": "XPS 13", "description": "13 inch laptop", "price": 999, "stock": "Available"}}
]

Important: Return ONLY the Python list, no other text or formatting."""
        
        formatted_prompt = prompt.format(text=text[:3000])  # Limit text length
        
        print("Calling Groq API to parse document...")
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": formatted_prompt}],
            temperature=0.1,
            max_tokens=2000
        )
        
        response_text = response.choices[0].message.content
        print(f"Raw response: {response_text[:200]}...")
        
        parsed_response = clean_and_parse_response(response_text)
        print(f"Successfully parsed {len(parsed_response)} products")
        return parsed_response
        
    except Exception as e:
        print(f"Error parsing document with Groq: {e}")
        return []

def extract_from_pdf(pdf_path: str) -> str:
    """Extract text from PDF."""
    try:
        text = ""
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        print(f"Extracted {len(text)} characters from PDF: {pdf_path}")
        return text
    except Exception as e:
        print(f"Error extracting text from PDF {pdf_path}: {e}")
        return ""

def index_catalogs():
    """Dynamically index catalogs using Groq to infer schema."""
    print("Starting catalog indexing...")
    chroma_db = ChromaDB()
    catalog_dir = "data/catalogs"
    
    if not os.path.exists(catalog_dir):
        print(f"ERROR: Catalog directory {catalog_dir} does not exist!")
        return
    
    print(f"Scanning catalog directory: {catalog_dir}")
    files = os.listdir(catalog_dir)
    print(f"Found {len(files)} files: {files}")
    
    documents = []
    for file in files:
        file_path = os.path.join(catalog_dir, file)
        print(f"\nProcessing file: {file}")
        
        if file.endswith(".xlsx"):
            try:
                df = pd.read_excel(file_path)
                text = df.to_string()
                print(f"Excel file loaded with {len(df)} rows")
                parsed_documents = infer_schema_and_parse(text)
                documents.extend(parsed_documents)
            except Exception as e:
                print(f"Error processing Excel file {file}: {e}")
        elif file.endswith(".pdf"):
            text = extract_from_pdf(file_path)
            if text:
                parsed_documents = infer_schema_and_parse(text)
                documents.extend(parsed_documents)
    
    print(f"\nTotal documents to index: {len(documents)}")
    if documents:
        try:
            chroma_db.index_documents(documents)
            print("Successfully indexed all documents!")
        except Exception as e:
            print(f"Error indexing documents: {e}")
    else:
        print("No documents were parsed successfully.")

if __name__ == "__main__":
    index_catalogs()