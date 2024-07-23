import openai
import os


def answer_gpt(user_content):
    openai.api_key = os.environ.get('GPT_API_KEY')

    messages = [
        {"role": "system", "content": "읽고 정리해서 출력해줘"},
        {"role": "user", "content": user_content}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    assistant_content = response['choices'][0]['message']['content']

    return assistant_content
