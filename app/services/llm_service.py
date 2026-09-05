import os

from dotenv import load_dotenv
from groq import Groq


load_dotenv()


client = Groq(api_key=os.getenv("GROQ_API_KEY"))


MODEL_NAME = "llama-3.3-70b-versatile"


def generate_answer(question: str, context: str) -> str:

    system_prompt = """
		You are a document question-answering assistant.

		Answer the user's question using ONLY the provided document context.

		Rules:
		1. Do not use outside knowledge.
		2. Do not invent information.
		3. If the answer cannot be found in the provided context,
		   just say:
		   "I could not find the answer in the provided documents."
		4. Keep the answer concise and accurate.
	"""

    user_prompt = f"""
		DOCUMENT CONTEXT:	{context}
		USER QUESTION:	{question}
		"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0,
    )

    return response.choices[0].message.content
