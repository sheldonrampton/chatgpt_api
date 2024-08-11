"""
vision3.py: uses the API to compare two different images

For more information:
https://platform.openai.com/docs/guides/vision
"""

# Encodes an image and submits it to the API for interpretation.

import base64
from openai import OpenAI

client = OpenAI()

# Function to encode the image
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

# Path to your image
image_path = "PDRM0029.png"

# Getting the base64 string
base64_image = encode_image(image_path)
base64_image2 = encode_image("PDRM0043.png")

response = client.chat.completions.create(
  model="gpt-4o-mini",
  messages=[
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "What are in these images? Is there any difference between them?",
        },
        {
          "type": "image_url",
          "image_url": {
            "url": f"data:image/jpeg;base64,{base64_image}"
          },
        },
        {
          "type": "image_url",
          "image_url": {
            "url": f"data:image/jpeg;base64,{base64_image2}"
          },
        },
      ],
    }
  ],
  max_tokens=300,
)
print(response.choices[0])


# print(response.choices[0])
# print(response.json())
print(response.choices[0].message.content)