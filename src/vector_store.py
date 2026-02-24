import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import streamlit as st

DATA_FOLDER = "data"
INDEX_FOLDER = "vector_index"

# Cache the model to avoid reloading on every interaction
@st.cache_resource
def get_model():
    return SentenceTransformer("all-MiniLM-L6-v2")

model = get_model()


def load_all_text_files():
    documents = []

    for filename in os.listdir(DATA_FOLDER):
        if filename.endswith(".txt"):
            with open(os.path.join(DATA_FOLDER, filename), "r", encoding="utf-8") as f:
                content = f.read()
                documents.append(content)

    return documents


def build_and_save_index():
    print("Loading clothing data...")
    documents = load_all_text_files()

    print("Generating embeddings...")
    embeddings = model.encode(documents)

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings))

    if not os.path.exists(INDEX_FOLDER):
        os.makedirs(INDEX_FOLDER)

    faiss.write_index(index, f"{INDEX_FOLDER}/index.faiss")
    np.save(f"{INDEX_FOLDER}/metadata.npy", np.array(documents, dtype=object))

    print("✅ Vector store built successfully!")


def load_index():
    index = faiss.read_index(f"{INDEX_FOLDER}/index.faiss")
    documents = np.load(f"{INDEX_FOLDER}/metadata.npy", allow_pickle=True)
    return index, documents


def search(query, k=2):
    index, documents = load_index()

    query_embedding = model.encode([query])
    distances, indices = index.search(np.array(query_embedding), k)

    results = [documents[i] for i in indices[0]]
    return results


if __name__ == "__main__":
    build_and_save_index()
