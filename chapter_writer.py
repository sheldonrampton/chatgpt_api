"""
First stab at at a Chatbot that writes an entire book chapter.
This produces a verbose chapter with a lot of redundancy.
"""


from openai import OpenAI # for calling the OpenAI API

# Set your API key here
openai_client = OpenAI(
  organization='org-M7JuSsksoyQIdQOGaTgA2wkk',
  project='proj_E0H6uUDUEkSZfn0jdmqy206G',
)

def generate_chapter_outline(description):
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Generate a detailed outline for a chapter based on this description: {description}. Include subheads with several bullet points under each subhead."}
        ],
        temperature=0
    )
    response_message = response.choices[0].message.content
    return response_message

def expand_bullet_point(bullet_point):
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Write 10 to 20 paragraphs expanding on this bullet point: {bullet_point}"}
        ],
        temperature=0
    )
    response_message = response.choices[0].message.content
    return response_message

def write_chapter(description):
    outline = generate_chapter_outline(description)
    print("Chapter Outline:")
    print(outline)

    # Split the outline into subheads and bullet points
    # Here we assume the outline is in a specific format. You might need to customize this based on the output you receive
    sections = outline.split("\n\n")
    chapter_content = ""

    for section in sections:
        subhead, *bullet_points = section.split("\n")
        chapter_content += f"\n\n## {subhead}\n"
        for bullet_point in bullet_points:
            expansion = expand_bullet_point(bullet_point.strip('- '))
            chapter_content += f"\n\n### {bullet_point}\n{expansion}"

    return chapter_content

# Example usage
description = "I want a chapter on the impacts of climate change on global agriculture."
chapter = write_chapter(description)
print(chapter)
