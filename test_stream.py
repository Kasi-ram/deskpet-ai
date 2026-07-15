from services.gemini_service import GeminiService

gemini = GeminiService()

for token in gemini.stream(
    "Explain what Retrieval Augmented Generation is in 100 words."
):
    print(token, end="", flush=True)