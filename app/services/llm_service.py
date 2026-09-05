import os

from dotenv import load_dotenv
from groq import Groq


load_dotenv()


client = Groq(api_key=os.getenv("GROQ_API_KEY"))


MODEL_NAME = "openai/gpt-oss-120b"

def generate_answer(question: str, context: str) -> str:

	system_prompt = """
		You are a document question-answering assistant.

		Answer the user's question using ONLY the provided document context.

		Rules:

		1. Use only information from the provided context.
		2. Do not use outside knowledge.
		3. Do not invent information.
		4. If the answer cannot be found in the context, say:
	   		"I could not find the answer in the provided documents."
		5. When making a factual claim, cite the relevant source
	  		using its source identifier, for example [SOURCE 1].
		6. Do not create source identifiers that are not present
	   		in the provided context.
		7. Keep the answer concise and accurate.
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
