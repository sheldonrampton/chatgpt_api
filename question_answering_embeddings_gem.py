"""
question_answering_embeddings_gem.py:
Answers questions based on GEM wiki-based embeddings generated in a CSV
file in embedding_gem_wiki.py

For more information:
https://cookbook.openai.com/examples/question_answering_using_embeddings
"""

# imports
import chatbotter as cb
from openai import OpenAI # for calling the OpenAI API
import pandas as pd  # for DataFrames to store article sections and embeddings


openai_client = OpenAI(
  organization='org-M7JuSsksoyQIdQOGaTgA2wkk',
  project='proj_E0H6uUDUEkSZfn0jdmqy206G',
)

# download pre-chunked text and pre-computed embeddings
embeddings_path = "data/embedding_gem_wiki.csv"
embedder = cb.Embedder(openai_client)
df = embedder.load_embeddings_from_csv(embeddings_path)

print(embedder.ask('Where is the SUKELCO Solar Power Plant located?', df))
print(embedder.ask('Tell me about the Peace River Area 2 Oil and Gas Project.', df))
print(embedder.ask('What coal-burning power plants have been retired since 2020?', df))
print(embedder.ask('Tell me about the Nelson Dewey Generating Facility.', df))
print(embedder.ask('What nonprofits in Wisconsin are advocating for renewable energy?', df))
print(embedder.ask('What companies in Wisconsin are investing in renewable energy?', df))
print(embedder.ask('What coal-burning power plants have been shut down in Wisconsin?', df))
print(embedder.ask('What coal-burning power plants have been retired since 2020?', df))
print(embedder.ask('What companies in Wisconsin are investing in renewable energy?', df))
print(embedder.ask('What are some solar power plants that are currently operating in Colorado?', df))
print(embedder.ask('Name some organizations that are advocating for renewable energy in the United States.', df))
print(embedder.ask('What are some front groups for the fossil fuel industry?', df))
print(embedder.ask('Describe the activities of the fossil fuel industry\'s front groups.', df))
print(embedder.ask('What are some effective ways to advocate for action on climate change?', df))
print(embedder.ask('Name some innovative businesses that are working to address climate change.', df))
print(embedder.ask('Tell me about Arch Coal.', df))
print(embedder.ask('What are some fossil fuel companies that have filed for bankruptcy?', df))
print(embedder.ask('I\'m working on a book about climate change and political polarization in the United States. Please review the articles in the GEM wiki and write an outline for a book chapter that will talk about organizations working to address the problem and the challenges that they are facing in today\'s political climate.', df))
