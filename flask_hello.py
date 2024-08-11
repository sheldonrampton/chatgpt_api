"""
* flask_hello.py: "Hello, world" test of Flask library
"""

from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"