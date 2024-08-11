"""
question_answering_embeddings_gem_flask.py:
Answers questions via a Flask-power chat web page,
based on the 10,000 GEM wiki embeddings generated using embedding_gem_wiki.py.

For more information:
https://cookbook.openai.com/examples/question_answering_using_embeddings
"""

# imports
from flask import Flask, request, jsonify, render_template
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


@app.route('/chat', methods=['POST'])
def chat():
    """Answers a query using GPT and a dataframe of relevant texts and embeddings."""
    model = "gpt-4"
    token_budget = 4096 - 500
    print_message = False
    query = request.json.get('message')
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
    return jsonify({'response': response_message})


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
