"""
vision.py:
a simple example of using the API to inspect an image from its URL and describe it

For more information:
https://platform.openai.com/docs/guides/vision
"""

from openai import OpenAI

client = OpenAI()

response = client.chat.completions.create(
  model="gpt-4o-mini",
  messages=[
    {
      "role": "user",
      "content": [
        {"type": "text", "text": "What’s in this image?"},
        {
          "type": "image_url",
          "image_url": {
            "url": "https://static.wixstatic.com/media/0c0801_42f4fec97e9a4b0783e2b1caabe3e3f5~mv2.png/v1/crop/x_0,y_174,w_2688,h_1259/fill/w_1880,h_880,al_c,q_90,usm_0.66_1.00_0.01,enc_auto/youth_tennis.png",
          },
        },
      ],
    }
  ],
  max_tokens=300,
)

print(response.choices[0])
