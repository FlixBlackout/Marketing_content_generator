from vector_store import search
from gemini_llm import generate_marketing_image


if __name__ == "__main__":
    user_query = input("Enter marketing request: ")

    # Step 1: Retrieve relevant brand context
    retrieved_chunks = search(user_query)

    print("\nRetrieved Context:\n", retrieved_chunks)

    # Step 2: Build final prompt
    final_prompt = f"""
    You are a professional fashion marketing designer.

    Brand Knowledge:
    {retrieved_chunks}

    Create a high-quality Instagram marketing image for:
    {user_query}

    Make it visually premium, modern, stylish.
    """

    print("\nFinal Prompt:\n", final_prompt)

    # Step 3: Generate Image
    generate_marketing_image(final_prompt)

