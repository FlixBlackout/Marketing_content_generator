👗 AI Fashion Marketing Content Generator

An AI-powered fashion marketing web application that generates high-quality promotional visuals using:

🔍 Retrieval Augmented Generation (RAG)

🧠 FAISS Vector Database

🤖 Sentence Transformers (Embeddings)

🎨 Replicate (FLUX Image Model)

🖥 Streamlit Frontend

This system creates brand-aware marketing images for:

Women’s Wear

Men’s Wear

Footwear

Seasonal Collections

Promotional Campaigns

🚀 Features

Brand-aware marketing image generation

FAISS-based semantic search (RAG pipeline)

Dynamic prompt construction

AI image generation via Replicate (FLUX model)

Clean Streamlit web interface

Automatic sequential image saving

Download generated images

Image history gallery

🏗 Project Structure
marketing_content_generator/
│
├── app.py                  # Streamlit frontend
├── vector_store.py         # FAISS + embedding pipeline
├── replicate_llm.py        # Image generation logic
├── .env                    # API keys
├── requirements.txt
│
├── data/                   # Brand knowledge base
│   ├── brand_profile.txt
│   ├── campaigns.txt
│   ├── audience_segments.txt
│   ├── womens_wear.txt
│   ├── mens_wear.txt
│   ├── footwear.txt
│   ├── seasonal_collections.txt
│   └── offers_and_pricing.txt
│
├── vector_index/           # Auto-generated FAISS index
│   ├── index.faiss
│   └── metadata.npy
│
└── generated_images/       # Generated marketing images
🧠 How It Works
1️⃣ Brand Knowledge Embedding

All .txt files inside the data/ folder are:

Loaded

Converted into embeddings using all-MiniLM-L6-v2

Stored in a FAISS vector index

2️⃣ Retrieval (RAG)

When a user enters a request like:

Create Instagram ad for summer women's dresses with 20% discount

The system:

Converts the query into an embedding

Searches FAISS for relevant brand data

Injects retrieved knowledge into the AI prompt

This ensures generated images stay consistent with the brand.

3️⃣ Image Generation

The enriched prompt is sent to:

black-forest-labs/flux-2-pro

via Replicate API to generate a 1024x1024 marketing image.

4️⃣ Output

Image is saved sequentially in generated_images/

Displayed in Streamlit

Downloadable via button

Recent image history shown in UI

🛠 Installation
1️⃣ Clone the Repository
git clone <your-repo-url>
cd marketing_content_generator
2️⃣ Create Virtual Environment (Recommended)
python3 -m venv venv
source venv/bin/activate
3️⃣ Install Dependencies
pip install -r requirements.txt
4️⃣ Add Replicate API Key

Create a .env file in the root directory:

REPLICATE_API_TOKEN=your_replicate_api_key_here

Get your API key from:
https://replicate.com/account/api-tokens

🧱 Build Vector Index (Important)

Before running the app, build the FAISS index:

python3 vector_store.py

This creates:

vector_index/
 ├── index.faiss
 └── metadata.npy

If you update files inside data/, delete the vector_index/ folder and rebuild.

▶️ Run the Application
streamlit run app.py

Then open:

http://localhost:8501
