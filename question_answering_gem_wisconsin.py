"""
question_answering_embeddings_gem.py:
Answers questions based on GEM wiki-based embeddings generated in a CSV
file in data/embedding_gem_wiki.py

For more information:
https://cookbook.openai.com/examples/question_answering_using_embeddings
"""

# imports
import chatbotter as cb
from openai import OpenAI # for calling the OpenAI API


openai_client = OpenAI(
  organization='org-M7JuSsksoyQIdQOGaTgA2wkk',
  project='proj_E0H6uUDUEkSZfn0jdmqy206G',
)

# download pre-chunked text and pre-computed embeddings
embeddings_path = "data/embedding_gem_wisconsin.csv"
embedder = cb.Embedder(openai_client)

asker = cb.Asker(openai_client)
asker.load_embeddings_from_csv(embeddings_path)
print(asker.ask('Who provides financing to the Nelson Dewey Generating Facility?'))
print(asker.ask('What are some activities in 2022 for RENEW Wisconsin?'))
print(asker.ask('Where is RENEW Wisconsin based?', model="gpt-4"))
print(asker.ask('Tell me about RENEW Wisconsin.', model="gpt-4o"))
print(asker.ask('What policies and programs does RENEW Wisconsin promote?'))
print(asker.ask('What is the mission of Clean Wisconsin?'))
print(asker.ask('Tell me about the Fraser Paper Power Plant.'))

