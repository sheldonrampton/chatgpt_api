# https://platform.openai.com/docs/quickstart

from openai import OpenAI
import json

client = OpenAI()

completion = client.chat.completions.create(
  model="gpt-4o",
  messages=[
    {"role": "system", "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."},
    {"role": "user", "content": "Compose a poem that explains the concept of recursion in programming."}
  ]
)

# print(completion.choices[0].message)
print(completion.choices[0].message.content)
print(json.dumps(dir(completion.choices[0].message), indent=1))
