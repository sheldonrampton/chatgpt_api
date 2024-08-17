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

asker = cb.Asker(openai_client, storage = storage)
print(asker.ask('What coal-burning power plants have been retired since 2020?')[0])
print(asker.ask('What coal-burning power plants have been retired since 2020?')[1])
print(asker.ask('What coal-burning power plants have been retired since 2020?')[2])
print(asker.ask('What companies in Wisconsin are investing in renewable energy?')[0])
print(asker.ask('What companies in Wisconsin are investing in renewable energy?')[1])
print(asker.ask('What companies in Wisconsin are investing in renewable energy?')[2])
print(asker.ask('What are some solar power plants that are currently operating in Colorado?')[0])
print(asker.ask('What are some solar power plants that are currently operating in Colorado?')[1])
print(asker.ask('What are some solar power plants that are currently operating in Colorado?')[2])
print(asker.ask('Name some organizations that are advocating for renewable energy in the United States.'))
print(asker.ask('What are some front groups for the fossil fuel industry?'))
print(asker.ask('Describe the activities of the fossil fuel industry\'s front groups.'))
print(asker.ask('What are some effective ways to advocate for action on climate change?'))
print(asker.ask('Name some innovative businesses that are working to address climate change.'))
print(asker.ask('Tell me about Arch Coal.'))
print(asker.ask('What are some fossil fuel companies that have filed for bankruptcy?'))
print(asker.ask('I\'m working on a book about climate change and political polarization in the United States. Please review the articles in the GEM wiki and write an outline for a book chapter that will talk about organizations working to address the problem and the challenges that they are facing in today\'s political climate.'))
