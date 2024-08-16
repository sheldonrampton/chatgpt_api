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
storage = cb.Storer(
    openai_client, None,
    db_path = 'gem_wiki.db',
    pinecone_index_name = 'gem-wiki-10000'
)

asker = cb.Asker(openai_client)
print(asker.ask_storage('What coal-burning power plants have been retired since 2020?', storage))
print(asker.ask_storage('What companies in Wisconsin are investing in renewable energy?', storage))
print(asker.ask_storage('What are some solar power plants that are currently operating in Colorado?', storage))
print(asker.ask_storage('Name some organizations that are advocating for renewable energy in the United States.', storage))
print(asker.ask_storage('What are some front groups for the fossil fuel industry?', storage))
print(asker.ask_storage('Describe the activities of the fossil fuel industry\'s front groups.', storage))
print(asker.ask_storage('What are some effective ways to advocate for action on climate change?', storage))
print(asker.ask_storage('Name some innovative businesses that are working to address climate change.', storage))
print(asker.ask_storage('Tell me about Arch Coal.', storage))
print(asker.ask_storage('What are some fossil fuel companies that have filed for bankruptcy?', storage))
print(asker.ask_storage('I\'m working on a book about climate change and political polarization in the United States. Please review the articles in the GEM wiki and write an outline for a book chapter that will talk about organizations working to address the problem and the challenges that they are facing in today\'s political climate.', storage))
