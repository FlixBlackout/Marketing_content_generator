import streamlit as st
from vector_store import search
from gemini_llm import generate_marketing_image


st.set_page_config(page_title="AI Fashion Marketing Generator", layout="wide")

st.title("👗 AI Fashion Marketing Content Generator")
st.markdown("Generate high-quality marketing visuals using AI + Brand Knowledge (RAG)")

# User Input
user_query = st.text_input("Enter your marketing request")

if st.button("Generate Marketing Image"):

    if user_query.strip() == "":
        st.warning("Please enter a marketing request.")
    else:
        with st.spinner("Retrieving brand knowledge..."):
            retrieved_chunks = search(user_query)

        st.subheader("🔎 Retrieved Brand Context")
        st.write(retrieved_chunks)

        # Build Prompt
        final_prompt = f"""
        You are a professional fashion marketing designer.

        Brand Knowledge:
        {retrieved_chunks}

        Create a high-quality Instagram marketing image for:
        {user_query}

        Make it visually premium, modern, stylish.
        """

        st.subheader("📝 Final AI Prompt")
        st.code(final_prompt)

        with st.spinner("Generating marketing image..."):
            image_url = generate_marketing_image(final_prompt)

        st.subheader("🖼 Generated Image")
        st.image(image_url, use_column_width=True)
