"""
embedding_test.py: creates a very simple embedding based on a single client message.
"""

from openai import OpenAI

client = OpenAI(
  organization='org-M7JuSsksoyQIdQOGaTgA2wkk',
  project='proj_E0H6uUDUEkSZfn0jdmqy206G',
)

response = client.embeddings.create(
  input="OpenAI is revolutionizing artificial intelligence.",
  model="text-embedding-ada-002"
)

embedding_vector = response.data[0].embedding
print(embedding_vector)
