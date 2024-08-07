# https://cookbook.openai.com/examples/question_answering_using_embeddings

# imports
import ast  # for converting embeddings saved as strings back to arrays
from openai import OpenAI # for calling the OpenAI API
import pandas as pd  # for storing text and embeddings data
import tiktoken  # for counting tokens
import os # for getting API token from env variable OPENAI_API_KEY
from scipy import spatial  # for calculating vector similarities for search
import json


# models
EMBEDDING_MODEL = "text-embedding-3-small"
GPT_MODEL = "gpt-3.5-turbo"

client = OpenAI(
  organization='org-M7JuSsksoyQIdQOGaTgA2wkk',
  project='proj_E0H6uUDUEkSZfn0jdmqy206G',
)

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


# download pre-chunked text and pre-computed embeddings
embeddings_path = "data/gem_wiki.csv"

df = pd.read_csv(embeddings_path)
# convert embeddings from CSV str type back to list type
df['embedding'] = df['embedding'].apply(ast.literal_eval)
# the dataframe has two columns: "text" and "embedding"
# print(df)

# search function
def strings_ranked_by_relatedness(
    query: str,
    df: pd.DataFrame,
    relatedness_fn=lambda x, y: 1 - spatial.distance.cosine(x, y),
    top_n: int = 100
) -> tuple[list[str], list[float]]:
    """Returns a list of strings and relatednesses, sorted from most related to least."""
    query_embedding_response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=query,
    )
    query_embedding = query_embedding_response.data[0].embedding
    strings_and_relatednesses = [
        (row["text"], relatedness_fn(query_embedding, row["embedding"]))
        for i, row in df.iterrows()
    ]
    strings_and_relatednesses.sort(key=lambda x: x[1], reverse=True)
    strings, relatednesses = zip(*strings_and_relatednesses)
    return strings[:top_n], relatednesses[:top_n]

# # examples of strings ranked by relatedness
# strings, relatednesses = strings_ranked_by_relatedness("Wisconsin", df, top_n=5)
# for string, relatedness in zip(strings, relatednesses):
#     print(f"{relatedness=:.3f}")
#     print(string)


def num_tokens(text: str, model: str = GPT_MODEL) -> int:
    """Return the number of tokens in a string."""
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))


def query_message(
    query: str,
    df: pd.DataFrame,
    model: str,
    token_budget: int
) -> str:
    """Return a message for GPT, with relevant source texts pulled from a dataframe."""
    strings, relatednesses = strings_ranked_by_relatedness(query, df)
    introduction = 'Use the below articles from the Global Energy Monitor wiki to answer questions. If the answer cannot be found in the articles, write "I could not find an answer."'
    question = f"\n\nQuestion: {query}"
    message = introduction
    for string in strings:
        next_article = f'\n\nGlobal Energy Monitor section:\n"""\n{string}\n"""'
        if (
            num_tokens(message + next_article + question, model=model)
            > token_budget
        ):
            break
        else:
            message += next_article
    return message + question


def ask(
    query: str,
    df: pd.DataFrame = df,
    model: str = GPT_MODEL,
    token_budget: int = 4096 - 500,
    print_message: bool = False,
) -> str:
    print("\nQuestion:", query)
    """Answers a query using GPT and a dataframe of relevant texts and embeddings."""
    message = query_message(query, df, model=model, token_budget=token_budget)
    if print_message:
        print(message)
    messages = [
        {"role": "system", "content": "You answer questions about sustainable energy in Wisconsin."},
        {"role": "user", "content": message},
    ]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0
    )
    response_message = response.choices[0].message.content
    return response_message

# Question about a facility
print(ask('What coal-burning power plants have been retired since 2020?', model="gpt-4"))
# Question about a facility
print(ask('Who provides financing to the Nelson Dewey Generating Facility?', model="gpt-4"))
# Activities for an organization
print(ask('What are some activities in 2022 for RENEW Wisconsin?', model="gpt-4"))
# Another RENEW Wisconsin question.
print(ask('Where is RENEW Wisconsin based?'))
# A more general question.
print(ask('Tell me about RENEW Wisconsin.'))
# Policies and programs
print(ask('What policies and programs does RENEW Wisconsin promote?'))
# comparison question
print(ask('What is the mission of Clean Wisconsin?'))
# Relationships
print(ask('What is the relationship between Clean Wisconsin and RENEW Wisconsin?'))
# Get a list of nonprofits
print(ask('What nonprofits in Wisconsin are advocating for renewable energy?'))
# Get a list of companies
print(ask('What companies in Wisconsin are investing in renewable energy?'))
# Coal plant shutdowns
print(ask('What coal-burning power plants have been shut down in Wisconsin?'))
# open-ended question
print(ask("How did COVID-19 affect Wisconsin?"))

