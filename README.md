# chatgpt_api
For testing the ChatGPT API

## Loading libraries
    source env/bin/activate

## Requirements
    pip3 freeze > requirements.txt

## Code
* assistant_test.py: a very simple assistant.
* assistant_test2.py: a more complicated assistant, with comments and output dumps showing the state of the various objects created by the API: agents, messages, etc.
  * creates a basic agent that answers queries
  * adds a code interpreter tool
  * adds a file_search tool and searches "Trust Us, We're Experts" to answer questions
  * parses annotations in the reply
  * adds a function calling tool that lets the assistant create a quiz, submit it to the user, and grade the answers.
  * displays JSON of objects include the assistant, runs, threads, messages, run steps, responses
* chat_completion.py: a very simple chat completion
* completion_test.py: another very simple chat completion
* embedding_gem_wiki: creates embeddings based on the first 10,000 articles in the GEM wiki (not the category: Wisconsin).
* embedding_gem_wisconsin.py: Generates embeddings from the GEM wiki for the category "Wisconsin"
* embedding_gem_wisconsin_sqlite.py: Generates embeddings from the GEM wiki for the category "Wisconsin," saves the embeddings in Pinecone, and saves the article segments in SQLite.
* embedding_test.py: creates a very simple embedding based on a single client message.
* flask_chatgpt.py: a simple proof-of-concept Flask app that uses the ChatGPT API to respond to users' requests. Uses files in the "static" and "templates" subdirectories
* function_calling.py: creates a chat completion (without an assistant) that calls a couple of functions to retrieve the data needed for its answers.
* flask_hello.py: "Hello, world" test of Flask library
* json_test.py: uses the chat API to return JSON
* mwclient_test.py: tests the allpages method in the mwclient library for accessing Mediawiki sites via their API.
* pinecone1.py: A simple example of using the Pinecone API to create an index.
* pinecone2.py: An example of using the Pinecone API to store embeddings with title and URL metadata and search them for similarity to a query string.
* pinecone3.py: An example of using the Pinecone API to search previously-saved embeddings and retrieve them including their metadata.
* pymediawiki.py: Test of the mediawiki (pymediawiki) to search the GEM wiki. The mwclient library doesn't have an obvious way to find the URLs of wiki pages, so I'm using this for that.
* question_answering_embeddings.py: The beginnings of a script that adds knowledge to ChatGPT using embeddings so it can answer specialized questions. This script doesn't actually create embeddings. It just creates a query with the actual text of a Wikipedia article included in the query.
* question_answering_embeddings2.py: Completion of the script to answer questions with the embeddings created by embedding_wikipedia.py. Loads the embeddings from a CSV file and uses them to answer a few questions.
* question_answering_embeddings2_flask.py: Loads embeddings from a CSV file and uses them in a Flask-powered chatbot that can answer questions.
* question_answering_embeddings_gem.py: Answers questions based on GEM wiki-based embeddings generated in a CSV file in embedding_gem_wiki.py.
* question_answering_embeddings_gem_flask.py: Answers questions via a Flask-power chat web page, based on the 10,000 GEM wiki embeddings generated using embedding_gem_wiki.py.
* question_answering_wisconsin_sqlite.py: Answers questions with the embeddings created by embedding_gem_wisconsin.py. Uses the embeddings in Pinecone and uses sqlite to look up the article segments.
* question_answering_wi_pinecone_sqlite_flask.py: Runs a Flask-powered chatbot that answers questions with the embeddings created by embedding_gem_wisconsin.py. Uses the embeddings in Pinecone and uses sqlite to look up the article segments.
* quickstart.py: a very simple chat completion
* vision.py: a simple example of using the API to inspect an image from its URL and describe it
* vision2.py: this time it encodes a local image and shares that via the API
* vision3.py: uses the API to compare two different images

## API documentation
https://github.com/openai/openai-python/blob/main/api.md