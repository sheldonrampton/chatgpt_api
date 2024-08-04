from flask import Flask, request, jsonify, render_template
from openai import OpenAI

client = OpenAI(
  organization='org-M7JuSsksoyQIdQOGaTgA2wkk',
  project='proj_E0H6uUDUEkSZfn0jdmqy206G',
)

app = Flask(__name__)

@app.route("/")
def home():
    return render_template('index.html')


# def hello_world1():
#     completion = client.chat.completions.create(
#       model="gpt-4o",
#       messages=[
#         {"role": "system", "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."},
#         {"role": "user", "content": "Compose a poem that explains the concept of recursion in programming."}
#       ]
#     )
#     print(completion.choices[0].message.content)
#     return jsonify({'response': completion.choices[0].message.content})


@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    completion = client.chat.completions.create(
      model="gpt-4o",
      messages=[
        {"role": "system", "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."},
        {"role": "user", "content": user_message}
      ]
    )
    return jsonify({'response': completion.choices[0].message.content})


if __name__ == '__main__':
    app.run(debug=True)
