"""
* pinecone2.py:
An example of using the Pinecone API to store embeddings with title and URL metadata
and search them for similarity to a query string.

For more information:
https://cookbook.openai.com/examples/vector_databases/pinecone/using_pinecone_for_embeddings_search
"""

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

article_df = pd.read_csv('../data/vector_database_wikipedia_articles_embedded.csv')
print(article_df.head())

# Read vectors from strings back into a list
article_df['title_vector'] = article_df.title_vector.apply(literal_eval)
article_df['content_vector'] = article_df.content_vector.apply(literal_eval)
# article_df['metadata'] = { "title": article_df.title, "url": article_df.content }

# Set vector_id to be a string
article_df['vector_id'] = article_df['vector_id'].apply(str)

print(article_df.head())
print(article_df.info(show_counts=True))

pinecone_api_key = os.environ.get('PINECONE_API_KEY')
# pinecone.init(api_key=api_key)
pinecone = Pinecone(api_key=pinecone_api_key)


# Models a simple batch generator that make chunks out of an input DataFrame
class BatchGenerator:
    
    def __init__(self, batch_size: int = 10) -> None:
        self.batch_size = batch_size
    
    # Makes chunks out of an input DataFrame
    def to_batches(self, df: pd.DataFrame) -> Iterator[pd.DataFrame]:
        splits = self.splits_num(df.shape[0])
        if splits <= 1:
            yield df
        else:
            for chunk in np.array_split(df, splits):
                yield chunk

    # Determines how many chunks DataFrame contains
    def splits_num(self, elements: int) -> int:
        return round(elements / self.batch_size)
    
    __call__ = to_batches

df_batcher = BatchGenerator(200)

# Pick a name for the new index
index_name = 'wikipedia-articles-2'

# Check whether the index with the same name already exists - if so, delete it
if index_name in pinecone.list_indexes():
    pinecone.delete_index(index_name)
    
# Creates new index
spec = ServerlessSpec(
    cloud="aws",
    region="us-east-1"
)

# check if index already exists (it shouldn't if this is your first run)
if index_name not in pinecone.list_indexes().names():
    # if does not exist, create index
    pinecone.create_index(
        index_name,
        dimension=len(article_df['content_vector'][0]),
        metric='cosine',
        spec=spec
    )
    # wait for index to be initialized
    while not pinecone.describe_index(index_name).status['ready']:
        time.sleep(1)

# connect to index
index = pinecone.Index(index_name)
time.sleep(1)
# view index stats
print(index.describe_index_stats())
# Confirm our index was created
print(pinecone.list_indexes())

# Upsert content vectors in content namespace - this can take a few minutes
print("Uploading vectors to content namespace..")
for batch_df in df_batcher(article_df):
    index.upsert(vectors=zip(
        batch_df.vector_id, batch_df.content_vector,
        [{**a, **b} for a, b in zip(
            [{ "title": t } for t in batch_df.title ],
            [{ "url": u } for u in batch_df.url ])
        ]
    ), namespace='content')

# Upsert title vectors in title namespace - this can also take a few minutes
print("Uploading vectors to title namespace..")
for batch_df in df_batcher(article_df):
    index.upsert(vectors=zip(
        batch_df.vector_id, batch_df.title_vector,
        [{ "title": t } for t in batch_df.title ],
        [{ "url": u } for u in batch_df.url ])
    ), namespace='title')

# Check index size for each namespace to confirm all of our docs have loaded
print(index.describe_index_stats())

# First we'll create dictionaries mapping vector IDs to their outputs so we can retrieve the text for our search results
titles_mapped = dict(zip(article_df.vector_id,article_df.title))
content_mapped = dict(zip(article_df.vector_id,article_df.text))

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
                       'title': [titles_mapped[_id] for _id in ids],
                       'content': [content_mapped[_id] for _id in ids],
                       })
    
    counter = 0
    for k,v in df.iterrows():
        counter += 1
        print(f'{v.title} (score = {v.score})')
    
    print('\n')

    return df


query_output = query_article('modern art in Europe','title')
print(query_output)

content_query_output = query_article("Famous battles in Scottish history",'content')
print(content_query_output)