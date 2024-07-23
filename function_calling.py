# https://platform.openai.com/docs/guides/function-calling

# Uses the OpenAI function calling feature.

from openai import OpenAI
import json
import subprocess


client = OpenAI()

# Example dummy function hard coded to return the same weather
# In production, this could be your backend API or an external API
def get_current_weather(location, unit="fahrenheit"):
    """Get the current weather in a given location"""
    if "tokyo" in location.lower():
        return json.dumps({"location": "Tokyo", "temperature": "10", "unit": unit})
    elif "san francisco" in location.lower():
        return json.dumps({"location": "San Francisco", "temperature": "72", "unit": unit})
    elif "paris" in location.lower():
        return json.dumps({"location": "Paris", "temperature": "22", "unit": unit})
    else:
        return json.dumps({"location": location, "temperature": "unknown"})


def get_current_time(location):
    """Get the current time in a given location"""

    url = "http://worldtimeapi.org/api/timezone/America/Chicago"
    current_time = "2024-07-23T12:15:30.207675-05:00"
    if "tokyo" in location.lower():
        url = "http://worldtimeapi.org/api/timezone/Asia/Tokyo"
    elif "san francisco" in location.lower():
        url = "http://worldtimeapi.org/api/timezone/America/Los_Angeles"
    elif "paris" in location.lower():
        url = "http://worldtimeapi.org/api/timezone/Europe/Paris"

    # Execute the curl command to get the time data
    result = subprocess.run(['curl', url], capture_output=True, text=True)
    
    # Parse the JSON response
    if result.returncode == 0:
        time_data = json.loads(result.stdout)
        current_time = time_data['datetime']
    return json.dumps({"location": location, "time": current_time})


def run_conversation():
    # Step 1: send the conversation and available functions to the model
    messages = [{"role": "user", "content": "What's the weather and current time in San Francisco, Tokyo, and Paris?"}]
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_current_weather",
                "description": "Get the current weather in a given location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g. San Francisco, CA",
                        },
                        "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                    },
                    "required": ["location"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_current_time",
                "description": "Get the current time in a given location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g. San Francisco, CA",
                        }
                    },
                    "required": ["location"],
                },
            },
        }
    ]
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=tools,
        tool_choice="auto",  # auto is default, but we'll be explicit
    )
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls
    # Step 2: check if the model wanted to call a function
    if tool_calls:
        # Step 3: call the function
        # Note: the JSON response may not always be valid; be sure to handle errors
        available_functions = {
            "get_current_weather": get_current_weather,
            "get_current_time": get_current_time,
        }  # only one function in this example, but you can have multiple
        messages.append(response_message)  # extend conversation with assistant's reply
        # Step 4: send the info for each function call and function response to the model
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            if function_name == 'get_current_time':
                function_response = function_to_call(
                    location=function_args.get("location")
                )
            elif function_name == 'get_current_weather':
                function_response = function_to_call(
                    location=function_args.get("location"),
                    unit=function_args.get("unit"),
                )
            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            )  # extend conversation with function response
        second_response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
        )  # get a new response from the model where it can see the function response
        return second_response


print(run_conversation().choices[0].message.content)
# print(get_current_time("Tokyo"))
