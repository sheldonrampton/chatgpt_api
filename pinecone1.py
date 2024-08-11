"""
* pinecone1.py: A simple example of using the Pinecone API to create an index.
"""

from pinecone import Pinecone, ServerlessSpec
import time
import pandas as pd
import ast
import os
from openai import OpenAI
import numpy as np
import wget
from ast import literal_eval


# models
EMBEDDING_MODEL = "text-embedding-3-small"
GPT_MODEL = "gpt-3.5-turbo"

client = OpenAI(
  organization='org-M7JuSsksoyQIdQOGaTgA2wkk',
  project='proj_E0H6uUDUEkSZfn0jdmqy206G',
)

res = client.embeddings.create(
    input=[
        "Sample document text goes here",
        "there will be several phrases in each batch"
    ], model=EMBEDDING_MODEL
)
embeds = [record.embedding for record in res.data]
print(len(embeds))
print(len(embeds[0]))


pinecone_api_key = os.environ.get('PINECONE_API_KEY')
pc = Pinecone(api_key=pinecone_api_key)

spec = ServerlessSpec(cloud="aws", region="us-east-1")
index_name = 'semantic-search-openai'

# check if index already exists (it shouldn't if this is your first run)
if index_name not in pc.list_indexes().names():
    # if does not exist, create index
    pc.create_index(
        index_name,
        dimension=len(embeds[0]),  # dimensionality of text-embed-3-small
        metric='cosine',
        spec=spec
    )
    # wait for index to be initialized
    while not pc.describe_index(index_name).status['ready']:
        time.sleep(1)

# connect to index
index = pc.Index(index_name)
time.sleep(1)
# view index stats
print(index.describe_index_stats())

