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
embeddings_path = "data/embedding_gem_wiki.csv"
embedder = cb.Embedder(openai_client)

asker = cb.Asker(openai_client)
asker.load_embeddings_from_csv(embeddings_path)
print(asker.ask('Where is the SUKELCO Solar Power Plant located?'))
print(asker.ask('Tell me about the Peace River Area 2 Oil and Gas Project.'))
print(asker.ask('What coal-burning power plants have been retired since 2020?'))
print(asker.ask('Tell me about the Nelson Dewey Generating Facility.'))
print(asker.ask('What nonprofits in Wisconsin are advocating for renewable energy?'))
print(asker.ask('What companies in Wisconsin are investing in renewable energy?'))
print(asker.ask('What coal-burning power plants have been shut down in Wisconsin?'))
print(asker.ask('What coal-burning power plants have been retired since 2020?'))
print(asker.ask('What companies in Wisconsin are investing in renewable energy?'))
print(asker.ask('What are some solar power plants that are currently operating in Colorado?'))
print(asker.ask('Name some organizations that are advocating for renewable energy in the United States.'))
print(asker.ask('What are some front groups for the fossil fuel industry?'))
print(asker.ask('Describe the activities of the fossil fuel industry\'s front groups.'))
print(asker.ask('What are some effective ways to advocate for action on climate change?'))
print(asker.ask('Name some innovative businesses that are working to address climate change.'))
print(asker.ask('Tell me about Arch Coal.'))
print(asker.ask('What are some fossil fuel companies that have filed for bankruptcy?'))
print(asker.ask('I\'m working on a book about climate change and political polarization in the United States. Please review the articles in the GEM wiki and write an outline for a book chapter that will talk about organizations working to address the problem and the challenges that they are facing in today\'s political climate.'))
