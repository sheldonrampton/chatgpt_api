# https://cookbook.openai.com/examples/vector_databases/pinecone/using_pinecone_for_embeddings_search

from openai import OpenAI
from typing import List, Iterator
import pandas as pd
import numpy as np
import os
import wget
from ast import literal_eval
import time

# Pinecone's client library for Python
# import pinecone
from pinecone import Pinecone, ServerlessSpec

# I've set this to our new embeddings model, this can be changed to the embedding model of your choice
# EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_MODEL = "text-embedding-ada-002"

client = OpenAI(
  organization='org-M7JuSsksoyQIdQOGaTgA2wkk',
  project='proj_E0H6uUDUEkSZfn0jdmqy206G',
)

# Ignore unclosed SSL socket warnings - optional in case you get these errors
import warnings

warnings.filterwarnings(action="ignore", message="unclosed", category=ResourceWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

# embeddings_url = 'https://cdn.openai.com/API/examples/data/vector_database_wikipedia_articles_embedded.zip'

# # The file is ~700 MB so this will take some time
# wget.download(embeddings_url)
# import zipfile
# with zipfile.ZipFile("vector_database_wikipedia_articles_embedded.zip","r") as zip_ref:
#     zip_ref.extractall("../data")

pinecone_api_key = os.environ.get('PINECONE_API_KEY')
# pinecone.init(api_key=api_key)
pinecone = Pinecone(api_key=pinecone_api_key)


# Pick a name for the new index
index_name = 'wikipedia-articles-2'

# connect to index
index = pinecone.Index(index_name)
time.sleep(1)
# view index stats
print(index.describe_index_stats())
# Confirm our index was created
print(pinecone.list_indexes())

# Check index size for each namespace to confirm all of our docs have loaded
print(index.describe_index_stats())

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
        top_k=top_k,
        includeMetadata=True
    )

    # Print query results 
    print(f'\nMost similar results to {query} in "{namespace}" namespace:\n')
    if not query_result.matches:
        print('no query result')
    
    matches = query_result.matches
    ids = [res.id for res in matches]
    scores = [res.score for res in matches]
    metadatas = [res.metadata for res in matches]
    print("METADATAS")
    print(metadatas)
    df = pd.DataFrame({'id':ids, 
                       'score':scores,
                       'title': [m['title'] for m in metadatas],
                       # 'url': [m['url'] for m in metadatas],
                       })
    
    counter = 0
    for k,v in df.iterrows():
        counter += 1
        print(f'{v.title} (score = {v.score})')
    
    print('\n')

    return df


query_output = query_article('Mormon polygamists','title')
print(query_output)

content_query_output = query_article("solar energy",'content')
print(content_query_output)