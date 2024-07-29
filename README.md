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
* embedding_test.py: creates a very simple embedding based on a single client message.
* function_calling.py: creates a chat completion (without an assistant) that calls a couple of functions to retrieve the data needed for its answers.
* json_test.py: uses the chat API to return JSON
* quickstart.py: a very simple chat completion
* vision.py: a simple example of using the API to inspect an image from its URL and describe it
* vision2.py: this time it encodes a local image and shares that via the API
* vision3.py: uses the API to compare two different images

## API documentation
https://github.com/openai/openai-python/blob/main/api.md