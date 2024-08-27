from openai import OpenAI # for calling the OpenAI API
from social_data import SocialData
from chatbotter import Asker

# import sqlite3
# import datetime
# import re
# from bs4 import BeautifulSoup
# import os
# import pandas as pd
# import tiktoken  # for counting tokens
# from itertools import islice
# from pinecone import Pinecone, ServerlessSpec
# from chatbotter import BatchGenerator, Asker
# import warnings
# import hashlib
# import time

# Suppress specific DeprecationWarnings
# warnings.filterwarnings("ignore", category=DeprecationWarning)


# Create the "months" directory if it doesn't exist
openai_client = OpenAI(
  organization='org-M7JuSsksoyQIdQOGaTgA2wkk',
  project='proj_E0H6uUDUEkSZfn0jdmqy206G',
)
sd = SocialData(openai_client)
sd.setup_pinecone()
# print(sd.query_article('Portage tennis','content'))
# print(sd.query_article('Expert in Artificial Intelligence','content'))

asker = Asker(openai_client, storage = sd,
    introduction = 'Use the below messages which were written by Sheldon Rampton to answer questions as though you are Sheldon Rampton. If the answer cannot be found in the articles, write "I could not find an answer."',
    string_divider = 'Messages:'
)
response, references, articles = asker.ask("Tell me about Portage tennis.")
print(response)

response, references, articles = asker.ask("What have you been doing with regard to artificial intelligence?")
print(response)

