"""
* embedding_gem_wiki: creates embeddings based on the first 10,000 articles
in the GEM wiki (not the category: Wisconsin).

Uses the chatbotter library.

For more information, see:
https://cookbook.openai.com/examples/embedding_wikipedia_articles_for_search
"""

# imports
import chatbotter as cb
from openai import OpenAI # for calling the OpenAI API
import pandas as pd  # for DataFrames to store article sections and embeddings


# limit = 20
extractor = cb.WikiExtractor()
wiki_strings, urls = extractor.compile_wiki_strings(categories = 'Wisconsin')
openai_client = OpenAI(
    organization='org-M7JuSsksoyQIdQOGaTgA2wkk',
    project='proj_E0H6uUDUEkSZfn0jdmqy206G'
)
embedder = cb.Embedder(openai_client)
df = embedder.compile_embeddings(wiki_strings, urls)
df2 = pd.DataFrame({"text": df.text, "embedding": df.embedding})
print(df2)
SAVE_PATH = "data/embedding_gem_wisconsin.csv"
df2.to_csv(SAVE_PATH, index=False)
