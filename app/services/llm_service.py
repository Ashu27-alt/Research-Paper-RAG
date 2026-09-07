"""Service for generating answers using the Groq LLM."""

from groq import Groq

from app.config import settings


# -------------------------
# 1. Initialize Groq client
# -------------------------

client = Groq(
    api_key=settings.groq_api_key
)


# -------------------------
# 2. Generate answer
# -------------------------

def generate_answer(question: str, context: str) -> str:
    """Generate a grounded answer using the provided document context."""

    system_prompt = """
    You are a document question-answering assistant.

    Answer the user's question using ONLY the provided document context.

    CITATION RULES:

    1. Every factual claim must be supported by the provided context.

    2. After each factual claim, include the source that directly
       supports that claim.

    3. Use citations in this exact format:

       [SOURCE 1]

       or, when multiple sources directly support the same claim:

       [SOURCE 1][SOURCE 2]

    4. Only cite a SOURCE if the information needed for the claim
       actually appears in that source.

    5. Do NOT cite a source merely because it is related to the topic.

    6. Do NOT invent source numbers.

    7. Do NOT cite sources that do not directly support the claim.

    8. If the provided context does not contain enough information to
       answer the question, say:

       "I could not find the answer in the provided documents."

    9. Prefer the smallest number of sources necessary to support
       each claim.

    10. Do not use outside knowledge.

    11. Keep the answer concise and accurate.

    12. Do not mention these citation rules in your answer.
    """

    user_prompt = f"""
    DOCUMENT CONTEXT:

    {context}

    USER QUESTION:

    {question}
    """

    response = client.chat.completions.create(
        model=settings.groq_model,
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        temperature=0,
    )

    return response.choices[0].message.content