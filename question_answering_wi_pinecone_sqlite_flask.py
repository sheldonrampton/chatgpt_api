"""
question_answering_gem_pinecone_sqlite_flask.py:
Runs a Flask-powered chatbot that answers questions using embeddings
extracted from both the GEM wiki and Wikipedia.

To run:
flask --app question_answering_wi_pinecone_sqlite_flask run

For more information see:
https://cookbook.openai.com/examples/embedding_wikipedia_articles_for_search
"""

from flask import Flask, request, jsonify, render_template
import chatbotter as cb
from openai import OpenAI # for calling the OpenAI API


openai_client = OpenAI(
  organization='org-M7JuSsksoyQIdQOGaTgA2wkk',
  project='proj_E0H6uUDUEkSZfn0jdmqy206G',
)
storage = cb.Storer(
    openai_client, None,
    db_path = 'wikipedia-climate-change.db',
    pinecone_index_name = 'wikipedia-climate-change'
)
wiki_asker = cb.Asker(openai_client, storage = storage)

storage_gem = cb.Storer(
    openai_client, None,
    db_path = 'gem_wiki.db',
    pinecone_index_name = 'gem-wiki-10000'
)
gem_asker = cb.Asker(openai_client, storage = storage_gem)


app = Flask(__name__)

@app.route("/")
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    """Answers a query using GPT and a dataframe of relevant texts and embeddings."""
    # model = "gpt-4"
    # token_budget = 4096 - 500
    # print_message = True
    query = request.json.get('message')
    wiki_response, wiki_references, wiki_articles = wiki_asker.ask(query)
    gem_response, gem_references, gem_articles = gem_asker.ask(query)

    response = "<b>GEM Wiki response:</b><br>" + gem_response + gem_references + "<br><br>"
    response += "<b>Wikipedia response:</b><br>" + wiki_response + wiki_references 

    return jsonify({'response': response})


if __name__ == '__main__':
    app.run(debug=True)

# Questions to ask:

# What coal-burning power plants have been retired since 2020?
# What companies in Wisconsin are investing in renewable energy?
# What are some solar power plants that are currently operating in Colorado?
# Name some organizations that are advocating for renewable energy in the United States.
# What are some front groups for the fossil fuel industry?
# Describe the activities of the fossil fuel industry's front groups.
# What are some effective ways to advocate for action on climate change?
# Name some innovative businesses that are working to address climate change.
# Tell me about Arch Coal.
# What are some fossil fuel companies that have filed for bankruptcy?
# I'm working on a book about climate change and political polarization in the United States. Please review the articles in the GEM wiki and write an outline for a book chapter that will talk about organizations working to address the problem and the challenges that they are facing in today\'s political climate.







