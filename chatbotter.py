"""
embedding_gem_pinecone_sqlite.py:
Generates embeddings from the GEM wiki, saves the embeddings in Pinecone,
and saves the article segments in sqlite.

For more information see:
https://cookbook.openai.com/examples/embedding_wikipedia_articles_for_search
"""

# imports
from openai import OpenAI # for calling the OpenAI API

import mwclient  # for downloading example Wikipedia articles
from typing import List, Iterator
from mediawiki import MediaWiki
import mwparserfromhell  # for splitting Wikipedia articles into sections
import os  # for environment variables
import pandas as pd  # for DataFrames to store article sections and embeddings
import re  # for cutting <ref> links out of Wikipedia articles
import tiktoken  # for counting tokens
from pinecone import Pinecone, ServerlessSpec
import hashlib
import time
import numpy as np
import sqlite3
import itertools


def unwanted_sections():
    return [
        "See also",
        "References",
        "External links",
        "Further reading",
        "Footnotes",
        "Bibliography",
        "Sources",
        "Citations",
        "Literature",
        "Footnotes",
        "Notes and references",
        "Photo gallery",
        "Works cited",
        "Photos",
        "Gallery",
        "Notes",
        "References and sources",
        "References and notes",
    ]


# OpenAI configuration
organization='org-M7JuSsksoyQIdQOGaTgA2wkk'
project='proj_E0H6uUDUEkSZfn0jdmqy206G'
GPT_MODEL = "gpt-3.5-turbo"  # selects which tokenizer to use
EMBEDDING_MODEL = "text-embedding-3-small"

# mwclient configuration
CATEGORY_TITLE = "Category:Wisconsin"
WIKI_SITE = "www.gem.wiki"
allpages_limit=50
SECTIONS_TO_IGNORE = unwanted_sections()

# mw_for_titles configuration
url='https://www.gem.wiki/w/api.php'
user_agent='sheldon-ramptons-agent'

# sqlite configuration
SQLITE_DB = 'gem_wiki_50.db'

# Pinecone configuration
pinecone_api_key = os.environ.get('PINECONE_API_KEY')
index_name = 'gem-wiki-50'


client = OpenAI(organization=organization, project=project)
site = mwclient.Site(WIKI_SITE)
gw = MediaWiki(url=url, user_agent=user_agent)
pinecone = Pinecone(api_key=pinecone_api_key)


def list_of_titles(
    pages: mwclient.listing, limit: int
) -> set[str]:
    """Return a set of page titles in a given Wiki category and its subcategories."""
    titles = set()
    urls = {}
    for page in itertools.islice(pages, limit):
        title = page.name
        titles.add(title)
        urls[title] = gw.opensearch(title, results=1)[0][2]
    return titles, urls




def all_subsections_from_section(
    section: mwparserfromhell.wikicode.Wikicode,
    parent_titles: list[str],
    sections_to_ignore: set[str],
) -> list[tuple[list[str], str]]:
    """
    From a Wikipedia section, return a flattened list of all nested subsections.
    Each subsection is a tuple, where:
        - the first element is a list of parent subtitles, starting with the page title
        - the second element is the text of the subsection (but not any children)
    """
    headings = [str(h) for h in section.filter_headings()]
    title = headings[0]
    if title.strip("=" + " ") in sections_to_ignore:
        # ^wiki headings are wrapped like "== Heading =="
        return []
    titles = parent_titles + [title]
    full_text = str(section)
    section_text = full_text.split(title)[1]
    if len(headings) == 1:
        return [(titles, section_text)]
    else:
        first_subtitle = headings[1]
        section_text = section_text.split(first_subtitle)[0]
        results = [(titles, section_text)]
        for subsection in section.get_sections(levels=[len(titles) + 1]):
            results.extend(all_subsections_from_section(subsection, titles, sections_to_ignore))
        return results


def all_subsections_from_title(
    title: str,
    sections_to_ignore: set[str] = SECTIONS_TO_IGNORE,
    site_name: str = WIKI_SITE,
) -> list[tuple[list[str], str]]:
    """From a Wikipedia page title, return a flattened list of all nested subsections.
    Each subsection is a tuple, where:
        - the first element is a list of parent subtitles, starting with the page title
        - the second element is the text of the subsection (but not any children)
    """
    site = mwclient.Site(site_name)
    page = site.pages[title]
    text = page.text()
    parsed_text = mwparserfromhell.parse(text)
    headings = [str(h) for h in parsed_text.filter_headings()]
    if headings:
        summary_text = str(parsed_text).split(headings[0])[0]
    else:
        summary_text = str(parsed_text)
    results = [([title], summary_text)]
    for subsection in parsed_text.get_sections(levels=[2]):
        results.extend(all_subsections_from_section(subsection, [title], sections_to_ignore))
    return results


# clean text
def clean_section(section: tuple[list[str], str]) -> tuple[list[str], str]:
    """
    Return a cleaned up section with:
        - <ref>xyz</ref> patterns removed
        - leading/trailing whitespace removed
    """
    titles, text = section
    text = re.sub(r"<ref.*?</ref>", "", text)
    text = text.strip()
    return (titles, text)



# filter out short/blank sections
def keep_section(section: tuple[list[str], str]) -> bool:
    """Return True if the section should be kept, False otherwise."""
    titles, text = section
    if len(text) < 16:
        return False
    else:
        return True


def num_tokens(text: str, model: str = GPT_MODEL) -> int:
    """Return the number of tokens in a string."""
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))


def halved_by_delimiter(string: str, delimiter: str = "\n") -> list[str, str]:
    """Split a string in two, on a delimiter, trying to balance tokens on each side."""
    chunks = string.split(delimiter)
    if len(chunks) == 1:
        return [string, ""]  # no delimiter found
    elif len(chunks) == 2:
        return chunks  # no need to search for halfway point
    else:
        total_tokens = num_tokens(string)
        halfway = total_tokens // 2
        best_diff = halfway
        for i, chunk in enumerate(chunks):
            left = delimiter.join(chunks[: i + 1])
            left_tokens = num_tokens(left)
            diff = abs(halfway - left_tokens)
            if diff >= best_diff:
                break
            else:
                best_diff = diff
        left = delimiter.join(chunks[:i])
        right = delimiter.join(chunks[i:])
        return [left, right]


def truncated_string(
    string: str,
    model: str,
    max_tokens: int,
    print_warning: bool = True,
) -> str:
    """Truncate a string to a maximum number of tokens."""
    encoding = tiktoken.encoding_for_model(model)
    encoded_string = encoding.encode(string)
    truncated_string = encoding.decode(encoded_string[:max_tokens])
    if print_warning and len(encoded_string) > max_tokens:
        print(f"Warning: Truncated string from {len(encoded_string)} tokens to {max_tokens} tokens.")
    return truncated_string


def split_strings_from_subsection(
    subsection: tuple[list[str], str],
    max_tokens: int = 10000,
    model: str = GPT_MODEL,
    max_recursion: int = 5,
) -> list[str]:
    """
    Split a subsection into a list of subsections, each with no more than max_tokens.
    Each subsection is a tuple of parent titles [H1, H2, ...] and text (str).
    """
    titles, text = subsection
    string = "\n\n".join(titles + [text])
    num_tokens_in_string = num_tokens(string)
    # if length is fine, return string
    if num_tokens_in_string <= max_tokens:
        return [string]
    # if recursion hasn't found a split after X iterations, just truncate
    elif max_recursion == 0:
        return [truncated_string(string, model=model, max_tokens=max_tokens)]
    # otherwise, split in half and recurse
    else:
        titles, text = subsection
        for delimiter in ["\n\n", "\n", ". "]:
            left, right = halved_by_delimiter(text, delimiter=delimiter)
            if left == "" or right == "":
                # if either half is empty, retry with a more fine-grained delimiter
                continue
            else:
                # recurse on each half
                results = []
                for half in [left, right]:
                    half_subsection = (titles, half)
                    half_strings = split_strings_from_subsection(
                        half_subsection,
                        max_tokens=max_tokens,
                        model=model,
                        max_recursion=max_recursion - 1,
                    )
                    results.extend(half_strings)
                return results
    # otherwise no split was found, so just truncate (should be very rare)
    return [truncated_string(string, model=model, max_tokens=max_tokens)]


def num_tokens(text: str, model: str = GPT_MODEL) -> int:
    """Return the number of tokens in a string."""
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))


def halved_by_delimiter(string: str, delimiter: str = "\n") -> list[str, str]:
    """Split a string in two, on a delimiter, trying to balance tokens on each side."""
    chunks = string.split(delimiter)
    if len(chunks) == 1:
        return [string, ""]  # no delimiter found
    elif len(chunks) == 2:
        return chunks  # no need to search for halfway point
    else:
        total_tokens = num_tokens(string)
        halfway = total_tokens // 2
        best_diff = halfway
        for i, chunk in enumerate(chunks):
            left = delimiter.join(chunks[: i + 1])
            left_tokens = num_tokens(left)
            diff = abs(halfway - left_tokens)
            if diff >= best_diff:
                break
            else:
                best_diff = diff
        left = delimiter.join(chunks[:i])
        right = delimiter.join(chunks[i:])
        return [left, right]


def truncated_string(
    string: str,
    model: str,
    max_tokens: int,
    print_warning: bool = True,
) -> str:
    """Truncate a string to a maximum number of tokens."""
    encoding = tiktoken.encoding_for_model(model)
    encoded_string = encoding.encode(string)
    truncated_string = encoding.decode(encoded_string[:max_tokens])
    if print_warning and len(encoded_string) > max_tokens:
        print(f"Warning: Truncated string from {len(encoded_string)} tokens to {max_tokens} tokens.")
    return truncated_string


def split_strings_from_subsection(
    subsection: tuple[list[str], str],
    max_tokens: int = 1000,
    model: str = GPT_MODEL,
    max_recursion: int = 5,
) -> list[str]:
    """
    Split a subsection into a list of subsections, each with no more than max_tokens.
    Each subsection is a tuple of parent titles [H1, H2, ...] and text (str).
    """
    titles, text = subsection
    string = "\n\n".join(titles + [text])
    num_tokens_in_string = num_tokens(string)
    # if length is fine, return string
    if num_tokens_in_string <= max_tokens:
        return [string]
    # if recursion hasn't found a split after X iterations, just truncate
    elif max_recursion == 0:
        return [truncated_string(string, model=model, max_tokens=max_tokens)]
    # otherwise, split in half and recurse
    else:
        titles, text = subsection
        for delimiter in ["\n\n", "\n", ". "]:
            left, right = halved_by_delimiter(text, delimiter=delimiter)
            if left == "" or right == "":
                # if either half is empty, retry with a more fine-grained delimiter
                continue
            else:
                # recurse on each half
                results = []
                for half in [left, right]:
                    half_subsection = (titles, half)
                    half_strings = split_strings_from_subsection(
                        half_subsection,
                        max_tokens=max_tokens,
                        model=model,
                        max_recursion=max_recursion - 1,
                    )
                    results.extend(half_strings)
                return results
    # otherwise no split was found, so just truncate (should be very rare)
    return [truncated_string(string, model=model, max_tokens=max_tokens)]


# Define a function to extract the first line
def get_first_line(text):
    return text.split('\n')[0]


def get_url(title):
    return urls[title]

def generate_vector_id(text: str) -> str:
    # Create a SHA256 hash object
    hash_object = hashlib.sha256()
    
    # Update the hash object with the text encoded in UTF-8
    hash_object.update(text.encode('utf-8'))
    
    # Return the hexadecimal digest of the hash, which is a string representation of the hash
    return hash_object.hexdigest()


pages = site.allpages()
titles, urls = list_of_titles(pages, limit=allpages_limit)
# split pages into sections
# may take ~1 minute per 100 articles
wikipedia_sections = []
for title in titles:
    wikipedia_sections.extend(all_subsections_from_title(title))
print(f"Found {len(wikipedia_sections)} sections in {len(titles)} pages.")
wikipedia_sections = [clean_section(ws) for ws in wikipedia_sections]
original_num_sections = len(wikipedia_sections)
wikipedia_sections = [ws for ws in wikipedia_sections if keep_section(ws)]
print(f"Filtered out {original_num_sections-len(wikipedia_sections)} sections, leaving {len(wikipedia_sections)} sections.")
# print example data
for ws in wikipedia_sections[:5]:
    print(ws[0])
    print(ws[1][:77] + "...")
    print()
# split sections into chunks
MAX_TOKENS = 1600
wikipedia_strings = []
for section in wikipedia_sections:
    wikipedia_strings.extend(split_strings_from_subsection(section, max_tokens=MAX_TOKENS))

print(f"{len(wikipedia_sections)} Wikipedia sections split into {len(wikipedia_strings)} strings.")


# print example data
print(wikipedia_strings[1])


BATCH_SIZE = 1000  # you can submit up to 2048 embedding inputs per request

embeddings = []
for batch_start in range(0, len(wikipedia_strings), BATCH_SIZE):
    batch_end = batch_start + BATCH_SIZE
    batch = wikipedia_strings[batch_start:batch_end]
    print(f"Batch {batch_start} to {batch_end-1}")
    response = client.embeddings.create(model=EMBEDDING_MODEL, input=batch)
    for i, be in enumerate(response.data):
        assert i == be.index  # double check embeddings are in same order as input
    batch_embeddings = [e.embedding for e in response.data]
    embeddings.extend(batch_embeddings)

df = pd.DataFrame({"text": wikipedia_strings, "embedding": embeddings})
df["title"] = df['text'].apply(get_first_line)
df["url"] = df['title'].apply(get_url)
df["vector_id"] = df['text'].apply(generate_vector_id)

for value in df['title']:
    print(value)
for value in df['url']:
    print(value)
for value in df['vector_id']:
    print(value)

conn = sqlite3.connect(SQLITE_DB)
c = conn.cursor()
c.execute('''
CREATE TABLE IF NOT EXISTS ArticleChunks (
    unique_id TEXT PRIMARY KEY,
    title TEXT,
    content TEXT,
    url TEXT
)
''')
conn.commit()
conn.close()




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
        dimension=len(df['embedding'][0]),
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
conn = sqlite3.connect(SQLITE_DB)
c = conn.cursor()
for batch_df in df_batcher(df):
    index.upsert(vectors=zip(
        batch_df.vector_id, batch_df.embedding,
        [{**a, **b} for a, b in zip(
            [{ "title": t } for t in batch_df.title ],
            [{ "url": u } for u in batch_df.url ])
        ]
    ), namespace='content')
    for rownum, row in batch_df.iterrows():
        c.execute('''
        INSERT INTO ArticleChunks (unique_id, title, content, url)
        VALUES (?, ?, ?, ?)
        ''', (row['vector_id'], row['title'], row['text'], row['url']))
        print("Inserted row ", rownum, row['title'])
conn.commit()
conn.close()
print("Records inserted successfully.")


# Check index size for each namespace to confirm all of our docs have loaded
print(index.describe_index_stats())

index = pinecone.Index(index_name)

# Now we'll create dictionaries mapping vector IDs to their outputs so we can retrieve the text for our search results
text_mapped = dict(zip(df.vector_id,df.text))
title_mapped = dict(zip(df.vector_id,df.title))

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
                       'text': [text_mapped[_id] for _id in ids],
                       'title': [title_mapped[_id] for _id in ids],
                       })
    
    counter = 0
    for k,v in df.iterrows():
        counter += 1
        print(f'{v.title} (score = {v.score})')
    
    print('\n')

    return df


query_output = query_article('Clean Coal','content')
print(query_output)

content_query_output = query_article("Wipperdorf",'content')
print(content_query_output)