"""
question_answering_gem_pinecone_sqlite_flask.py:
Runs a Flask-powered chatbot that answers questions with the embeddings
created by embedding_gem_pinecone_sqlite.py. Uses the embeddings in
Pinecone and uses sqlite to look up the article segments.

To run:
flask --app question_answering_gem_pinecone_sqlite_flask run

For more information see:
https://cookbook.openai.com/examples/embedding_wikipedia_articles_for_search
"""

# imports
from flask import Flask, request, jsonify, render_template
# import ast  # for converting embeddings saved as strings back to arrays
# from scipy import spatial  # for calculating vector similarities for search
# import json
import mwclient  # for downloading example Wikipedia articles
from typing import List, Iterator
from mediawiki import MediaWiki
import mwparserfromhell  # for splitting Wikipedia articles into sections
from openai import OpenAI # for calling the OpenAI API
import os  # for environment variables
import pandas as pd  # for DataFrames to store article sections and embeddings
import re  # for cutting <ref> links out of Wikipedia articles
import tiktoken  # for counting tokens
from pinecone import Pinecone, ServerlessSpec
import hashlib
import time
import numpy as np
import sqlite3


client = OpenAI(
  organization='org-M7JuSsksoyQIdQOGaTgA2wkk',
  project='proj_E0H6uUDUEkSZfn0jdmqy206G',
)

# gw = MediaWiki(
#     url='https://www.gem.wiki/w/api.php',
#     user_agent='sheldon-ramptons-agent'
# )

pinecone_api_key = os.environ.get('PINECONE_API_KEY')
pinecone = Pinecone(api_key=pinecone_api_key)
# index_name = 'gem-wiki-test'
index_name = 'gem-wiki-10000'
# connect to index
index = pinecone.Index(index_name)

# models
EMBEDDING_MODEL = "text-embedding-3-small"
GPT_MODEL = "gpt-3.5-turbo"

app = Flask(__name__)

@app.route("/")
def home():
    return render_template('index.html')

#### HELPER FUNCTIONS ###
# Format a JSON string so it is easy to read.
def show_json(obj):
    print(json.dumps(json.loads(obj.model_dump_json()), indent=2))


# Pretty printing helper
def pretty_print(messages):
    print("# Messages")
    for m in messages:
        print(f"{m.role}: {m.content[0].text.value}")
    print()


def get_article_chunk(unique_id):
    conn = sqlite3.connect('gem_wiki.db')
    cursor = conn.cursor()
    # SQL query to retrieve the row with the specified unique_id
    query = "SELECT title, url, content FROM ArticleChunks WHERE unique_id = ?"
    try:
        # Execute the query and fetch the row
        cursor.execute(query, (unique_id, ))
        row = cursor.fetchone()
        conn.close()

        # Check if a row was found
        if row:
            return row
        else:
            print(f"No row found with unique_id = {unique_id}")
            return None
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return None


# search function
def strings_ranked_by_relatedness(
    query: str,
    top_n: int = 100
) -> tuple[list[str], list[float]]:
    """Returns a list of strings and relatednesses, sorted from most related to least."""
    query_embedding_response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=query,
    )
    query_embedding = query_embedding_response.data[0].embedding

    res = client.embeddings.create(input=[query], model=EMBEDDING_MODEL)
    embedded_query = res.data[0].embedding

    # Query namespace passed as parameter using title vector
    query_result = index.query(
        namespace='content',
        vector=embedded_query,
        top_k=top_n
    )

    print(f'\nMost similar results to {query} in "content" namespace:\n')
    if not query_result.matches:
        print('no query result')
    
    matches = query_result.matches
    ids = [res.id for res in matches]
    scores = [res.score for res in matches]
    df = pd.DataFrame({'id':ids, 
                       'score':scores,
                       })
    
    df['title'], df['url'], df['content'] = zip(*df['id'].apply(lambda x: get_article_chunk(x)))

    counter = 0
    # for k,v in df.iterrows():
    #     counter += 1
    #     print(f'{v.title} (score = {v.score})')

    # print('\n')
    return df


def num_tokens(text: str, model: str = GPT_MODEL) -> int:
    """Return the number of tokens in a string."""
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))


def query_message(
    query: str,
    model: str,
    token_budget: int
) -> str:
    """Return a message for GPT, with relevant source texts pulled from a dataframe."""
    df = strings_ranked_by_relatedness(query)
    introduction = 'Use the below articles from the Global Energy Monitor wiki to answer questions. If the answer cannot be found in the articles, write "I could not find an answer."'
    question = f"\n\nQuestion: {query}"
    message = introduction
    articles = {}
    for k,v in df.iterrows():
        string = v.content
        title = v.title
        url = v.url
        articles[title] = url
        next_article = f'\n\nGlobal Energy Monitor section:\n"""\n{string}\n"""'
        if (
            num_tokens(message + next_article + question, model=model)
            > token_budget
        ):
            break
        else:
            message += next_article
    # print(articles)
    return message + question, articles


@app.route('/chat', methods=['POST'])
def chat():
    """Answers a query using GPT and a dataframe of relevant texts and embeddings."""
    model = "gpt-4"
    token_budget = 4096 - 500
    print_message = False
    query = request.json.get('message')
    message, articles = query_message(query, model=model, token_budget=token_budget)
    if print_message:
        print(message)
    messages = [
        {"role": "system", "content": "You answer questions about sustainable energy and other activities related to climate change and global warming."},
        {"role": "user", "content": message},
    ]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0
    )
    response_message = response.choices[0].message.content
    # print(response_message)

    references = "<p><b>For more information:</b></p><ul>"
    for title, url in articles.items():
        references += "<li><a href=\"" + url  + "\">" + title + "</a></li>"
    references += "</ul>"

    messages2 = [
        {"role": "system", "content": "You provide references to articles used to compile answers to questions from the GEM wiki."},
        {"role": "user", "content": references},
    ]
    response2 = client.chat.completions.create(
        model=model,
        messages=messages2,
        temperature=0
    )
    response_message2 = response2.choices[0].message.content

    return jsonify({'response': response_message + references})


if __name__ == '__main__':
    app.run(debug=True)

# Questions:

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
# I'm working on a book about climate change and political polarization in the United States. Please review the articles in the GEM wiki and write an outline for a book chapter that will talk about organizations working to address the problem and the challenges that they are facing in today's political climate.







