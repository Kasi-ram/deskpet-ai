from services.embedding_service import EmbeddingService

embedding_service = EmbeddingService()

text1 = "Cabin baggage is limited to 7 kg."

text2 = "Hand luggage maximum weight is 7 kilograms."

text3 = "The weather is rainy today."

embedding1 = embedding_service.embed(text1)
embedding2 = embedding_service.embed(text2)
embedding3 = embedding_service.embed(text3)

print("Embedding 1:", embedding1[:5])
print("Embedding 2:", embedding2[:5])
print("Embedding 3:", embedding3[:5])