# https://cookbook.openai.com/examples/assistants_api_overview_python

from openai import OpenAI
import json
import os
import time


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


## FUNCTIONS THAT WAIT FOR PROCESSES TO COMPLETE
def wait_on_run(run, thread):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.5)
        show_json(run)
    return run


def wait_on_files(file_batch):
    # print(file_batch.status)
    # print(file_batch.file_counts)
    while file_batch.file_counts.in_progress > 0:
        # print(file_batch.status)
        # print(file_batch.file_counts)
        time.sleep(0.5)


## FUNCTIONS THAT INTERACT WITH THE API

# Submit a user message to the assistant.
def submit_message(assistant_id, thread, user_message):
    client.beta.threads.messages.create(
        thread_id=thread.id, role="user", content=user_message
    )
    return client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id,
    )


# Get the response to a thread.
def get_response(thread):
    return client.beta.threads.messages.list(thread_id=thread.id, order="asc")


# Create a thread and run it within the assistant.
def create_thread_and_run(user_input):
    thread = client.beta.threads.create()
    run = submit_message(MATH_ASSISTANT_ID, thread, user_input)
    return thread, run


## HELPEF FUNCTIONS FOR THE display_quiz FUNCTION
# Get a response to a multiple-choice question.
def get_response_from_user_multiple_choice():
    results = input("Enter your choice: ")
    print("You chose", results)
    return results


# Get a response to an "essay question"
def get_response_from_user_free_response():
    results = input("Enter your answer: ")
    print("You chose", results)
    return results


# Display a quiz and get responses to each question in it.
def display_quiz(title, questions):
    print("Quiz:", title)
    print()
    responses = []

    for q in questions:
        print(q["question_text"])
        response = ""

        # If multiple choice, print options
        if q["question_type"] == "MULTIPLE_CHOICE":
            for i, choice in enumerate(q["choices"]):
                print(f"{choice}")
            response = get_response_from_user_multiple_choice()

        # Otherwise, just get response
        elif q["question_type"] == "FREE_RESPONSE":
            response = get_response_from_user_free_response()

        responses.append(response)
        print()

    return responses


# Create the OpenAI client.
client = OpenAI(
  organization='org-M7JuSsksoyQIdQOGaTgA2wkk',
  project='proj_E0H6uUDUEkSZfn0jdmqy206G',
)

# Use the client to create an assistant.
assistant = client.beta.assistants.create(
    name="Math Tutor",
    instructions="You are a personal math tutor. Answer questions briefly, in a sentence or less.",
    model="gpt-4o-mini",
)
MATH_ASSISTANT_ID = assistant.id
# show_json(assistant)

# Do some simple runs with the assistant.
# Emulating concurrent user requests
thread1, run1 = create_thread_and_run(
    "I need to solve the equation `3x + 11 = 14`. Can you help me?"
)
thread2, run2 = create_thread_and_run("Could you explain linear algebra to me?")
thread3, run3 = create_thread_and_run("I don't like math. What can I do?")


# Wait for Run 1
run1 = wait_on_run(run1, thread1)
pretty_print(get_response(thread1))

# Wait for Run 2
run2 = wait_on_run(run2, thread2)
pretty_print(get_response(thread2))

# Wait for Run 3
run3 = wait_on_run(run3, thread3)
pretty_print(get_response(thread3))

# Thank our assistant on Thread 3 :)
run4 = submit_message(MATH_ASSISTANT_ID, thread3, "Thank you!")
run4 = wait_on_run(run4, thread3)
pretty_print(get_response(thread3))

# Modify the assistant to add a code interpreter tool.
assistant = client.beta.assistants.update(
    MATH_ASSISTANT_ID,
    tools=[{"type": "code_interpreter"}],
)
show_json(assistant)

# Start another thread.
thread, run = create_thread_and_run(
    "Generate the first 20 fibbonaci numbers with code."
)
run = wait_on_run(run, thread)
pretty_print(get_response(thread))

# List the steps that were taken in the thread.
run_steps = client.beta.threads.runs.steps.list(
    thread_id=thread.id, run_id=run.id, order="asc"
)

for step in run_steps.data:
    step_details = step.step_details
    print(json.dumps(show_json(step_details), indent=4))

# Retrieve information from a file using the file_search tool.
# Create a vector store caled "Trust Us, We're Experts"
vector_store = client.beta.vector_stores.create(name="Sheldon's books")
 
# Ready the files for upload to OpenAI
file_paths = ["TUWE.pdf"]
file_streams = [open(path, "rb") for path in file_paths]
 
# Use the upload and poll SDK helper to upload the files, add them to the vector store,
# and poll the status of the file batch for completion.
file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
  vector_store_id=vector_store.id, files=file_streams
)

# Wait until the file is fully processed.
wait_on_files(file_batch)

# Update the assistant so it recognizes the file(s).
assistant = client.beta.assistants.update(
  assistant_id=assistant.id,
  instructions="You are a personal math tutor. Give expansive, detailed answers to questions.",
  tools=[{"type": "file_search"}],
  tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
)
show_json(assistant)

# Ask the assistant for information from the file.
thread, run = create_thread_and_run(
    "What does the book have to say about Edward Bernays?"
)
run = wait_on_run(run, thread)
pretty_print(get_response(thread))

# Enable function calling.
function_json = {
    "name": "display_quiz",
    "description": "Displays a quiz to the student, and returns the student's response. A single quiz can have multiple questions.",
    "parameters": {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "questions": {
                "type": "array",
                "description": "An array of questions, each with a title and potentially options (if multiple choice).",
                "items": {
                    "type": "object",
                    "properties": {
                        "question_text": {"type": "string"},
                        "question_type": {
                            "type": "string",
                            "enum": ["MULTIPLE_CHOICE", "FREE_RESPONSE"],
                        },
                        "choices": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["question_text"],
                },
            },
        },
        "required": ["title", "questions"],
    },
}

# Update the assistant to handle function calling.
assistant = client.beta.assistants.update(
    assistant_id=assistant.id,
    tools=[
        {"type": "code_interpreter"},
        {"type": "file_search"},
        {"type": "function", "function": function_json},
    ],
    tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
)
show_json(assistant)

# Have the assistant make the quiz.
thread, run = create_thread_and_run(
    "Make a quiz with 3 questions: One open ended, two multiple choice. Then, give me feedback for the responses."
)
run = wait_on_run(run, thread)
print(run.status)
show_json(run)

# Process the tool call(s) needed to run the function.
tool_calls = run.required_action.submit_tool_outputs.tool_calls
if tool_calls:
    # Call the function
    # Note: the JSON response may not always be valid; be sure to handle errors
    available_functions = {
        "display_quiz": display_quiz,
    }  # only one function in this example, but you can have multiple
    # messages.append(response_message)  # extend conversation with assistant's reply
    # Step 3: send the info for each function call and function response to the model
    for tool_call in tool_calls:
        function_name = tool_call.function.name
        function_to_call = available_functions[function_name]
        function_args = json.loads(tool_call.function.arguments)
        if function_name == 'display_quiz':
            function_response = function_to_call(
                title=function_args["title"],
                questions=function_args["questions"],
            )
        run = client.beta.threads.runs.submit_tool_outputs(
            thread_id=thread.id,
            run_id=run.id,
            tool_outputs=[
                {
                    "tool_call_id": tool_call.id,
                    "output": json.dumps(function_response),
                }
            ],
        )
        show_json(run)

        run = wait_on_run(run, thread)
        pretty_print(get_response(thread))
