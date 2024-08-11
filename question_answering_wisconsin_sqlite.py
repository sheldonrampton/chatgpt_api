"""
question_answering_wisconsin_sqlite.py:
Answers questions with the embeddings
created by embedding_gem_wisconsin.py. Uses the embeddings in
Pinecone and uses sqlite to look up the article segments.

For more information see:
https://cookbook.openai.com/examples/embedding_wikipedia_articles_for_search
"""

# imports
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

gw = MediaWiki(
    url='https://www.gem.wiki/w/api.php',
    user_agent='sheldon-ramptons-agent'
)

# get Wikipedia pages about the 2022 Winter Olympics

# CATEGORY_TITLE = "Category:2022 Winter Olympics"
# WIKI_SITE = "en.wikipedia.org"

CATEGORY_TITLE = "Category:Wisconsin"
WIKI_SITE = "www.gem.wiki"


GPT_MODEL = "gpt-3.5-turbo"  # only matters insofar as it selects which tokenizer to use
EMBEDDING_MODEL = "text-embedding-3-small"

conn = sqlite3.connect('gem_wiki.db')
cursor = conn.cursor()

pinecone_api_key = os.environ.get('PINECONE_API_KEY')
pinecone = Pinecone(api_key=pinecone_api_key)


# Pick a name for the new index
index_name = 'gem-wiki-test'
# connect to index
index = pinecone.Index(index_name)
# view index stats
print(index.describe_index_stats())
# Confirm our index exists
print(pinecone.list_indexes())

# Check index size for each namespace to confirm all of our docs have loaded
print(index.describe_index_stats())

# Now we'll create dictionaries mapping vector IDs to their outputs so we can retrieve the text for our search results
# text_mapped = dict(zip(df.vector_id,df.text))
# title_mapped = dict(zip(df.vector_id,df.title))

def get_article_chunk(unique_id):
    # SQL query to retrieve the row with the specified unique_id
    query = "SELECT title, url, content FROM ArticleChunks WHERE unique_id = ?"
    try:
        # Execute the query and fetch the row
        cursor.execute(query, (unique_id, ))
        row = cursor.fetchone()

        # Check if a row was found
        if row:
            return row
        else:
            print(f"No row found with unique_id = {unique_id}")
            return None
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return None


def query_article(query, namespace, top_k=5):
    '''Queries an article using its title in the specified
     namespace and prints results.'''

    # Use the OpenAI client to create vector embeddings based on the title column
    res = client.embeddings.create(input=[query], model=EMBEDDING_MODEL)
    embedded_query = res.data[0].embedding

    # Query namespace passed as parameter using title vector
    query_result = index.query(
        namespace=namespace,
        vector=embedded_query,
        top_k=top_k
    )

    # Print query results 
    print(f'\nMost similar results to {query} in "{namespace}" namespace:\n')
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
    for k,v in df.iterrows():
        counter += 1
        print(f'{v.title} (score = {v.score})')
    
    print('\n')
    return df


query_output = query_article('companies that are working on renewable energy','content')
print(query_output)

content_query_output = query_article("solar farm",'content')
print(content_query_output)

conn.close()
