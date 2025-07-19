VoltEdge Retail Chatbot
A privacy-preserving retail chatbot that searches a local product catalog and falls back to online searches using SerpApi. Built with ChromaDB for vector search, Groq for response generation, and Python 3.12.10.
Features

Local Catalog Search: Queries a local catalog (electronics_catalog.xlsx, electronics_catalog.pdf) with 100 products across 9 categories (e.g., Smartphones, Laptops) using ChromaDB.
Online Search Fallback: Uses SerpApi to fetch online results when local catalog results are insufficient.
Natural Language Responses: Generates responses using Groq’s llama-3.3-70b-versatile model.
Privacy-Preserving: Prioritizes local data to minimize external API calls.

Project Structure
retail_product_search/
├── data/
│   ├── catalogs/
│   │   ├── electronics_catalog.pdf
│   │   └── electronics_catalog.xlsx
├── src/
│   ├── mcp_server/
│   │   ├── __init__.py
│   │   ├── server.py
│   │   └── tools.py
│   ├── chatbot/
│   │   ├── __init__.py
│   │   └── chatbot.py
│   ├── rag/
│   │   ├── __init__.py
│   │   └── rag_pipeline.py
│   ├── vector_db/
│   │   ├── __init__.py
│   │   └── chroma_db.py
├── scripts/
│   ├── index_catalogs.py
├── requirements.txt
├── .env
├── README.md
└── main.py

Prerequisites

Python 3.12.10
uv (recommended for dependency management)
SerpApi account (free tier: 100 searches/month)
Groq account for API key

Setup

Clone the Repository:
git clone <repository-url>
cd retail_product_search


Set Up Virtual Environment:
uv venv
.venv\Scripts\activate


Install Dependencies:
set UV_LINK_MODE=copy
uv pip install -r requirements.txt


Dependencies: pandas, PyPDF2, langchain, chromadb, groq, python-dotenv, requests, sentence-transformers, openpyxl, jsonpatch.


Configure Environment Variables:

Create/edit .env in the project root:GROQ_API_KEY=your_groq_api_key_here
SERPAPI_KEY=your_serpapi_key_here
CHROMA_TELEMETRY_ENABLED=false
GROQ_PROXIES=
UV_LINK_MODE=copy


Obtain GROQ_API_KEY from Groq Console.
Obtain SERPAPI_KEY from SerpApi Dashboard.


Index the Catalog:
uv run python scripts/index_catalogs.py


Indexes data/catalogs/electronics_catalog.xlsx and data/catalogs/electronics_catalog.pdf into ChromaDB.



Usage

Run the Chatbot:
uv run python main.py


Interact with the Chatbot:

Enter queries like: Phones with 128GB storage and 5G support.
Example response:Response: Based on the local catalog:
- Samsung Galaxy S24: 128GB Storage, 6.2-inch Dynamic AMOLED 2X, 5G, Snapdragon 8 Gen 3, Triple Camera, Price: $699, In Stock
- Apple iPhone 15: 128GB Storage, 6.1-inch Super Retina XDR, 5G, A16 Bionic, Dual Camera, Price: $799, In Stock
- Google Pixel 8: 128GB Storage, 6.2-inch Actua Display, 5G, Tensor G3, Dual Camera, Price: $599, In Stock
- And more...
Would you like me to search again or refine the query?


Type exit to quit.



Troubleshooting

OneDrive Issues: The project is in C:\Users\sniki\OneDrive\Desktop\retail_product_search. OneDrive’s sync may cause filesystem errors (e.g., hardlink issues). Move the project to a local directory:move C:\Users\sniki\OneDrive\Desktop\retail_product_search C:\retail_product_search
cd C:\retail_product_search
.venv\Scripts\activate
uv pip install -r requirements.txt


SerpApi 401 Error: Ensure SERPAPI_KEY is valid in .env. Test with:python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('SERPAPI_KEY'))"


No Local Results: Reindex catalogs:rmdir /S /Q chroma
uv run python scripts/index_catalogs.py


Dependencies: Reinstall if issues persist:uv pip install --force-reinstall -r requirements.txt
