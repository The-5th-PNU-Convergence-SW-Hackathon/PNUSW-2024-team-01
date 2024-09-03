import os
from openai import OpenAI

# OpenAI 클라이언트 설정
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

def answer_gpt(user_content):
    messages = [
        {
            "role": "system",
            "content": (
        "Categorize the following text into the appropriate category and only state the category.\n"
        "Consider variations in wording and synonyms as matching the relevant category.\n"
        "If the text includes the keywords '공모전' or '경진대회', categorize it into the most appropriate [공모전] category.\n"
        "[Competition/Contest] Engineering/Information Technology/Software =([공모전] 공학/IT/SW)\n"
        "[Competition/Contest] Ideas/Planning =([공모전] 아이디어/기획)\n"
        "[Competition/Contest] Art/Design/Architecture =([공모전] 미술/디자인/건축)\n"
        "[Competition/Contest] Literature/Personal Narrative/Essay =([공모전] 문학/수기/에세이)\n"
        "[Competition/Contest] Miscellaneous (for contests not clearly falling into other categories or if uncertain) =([공모전] 기타)\n"
        "Kind of Education/Lecture/Program or International assignment/Exchange student including Survey Participation Invitation =(교육/특강/프로그램)\n"
        "Scholarship/Scholar (only those awarded, including work-study students) =(장학금)\n"
        "Supporters/Ambassadors =(서포터즈)\n"
        "Volunteer Work/Mentoring/Tutoring =(봉사활동)\n"
        "Employment Information/Job Fair/Recruitment Fair (only company hiring, excluding graduate school, dormitories, etc.) =(취업 정보)\n"
        "If the text is too short, unclear, or does not fit into any category, respond with 해당없음.\n"
        "If the text could fit into multiple categories, prioritize the most relevant category or the first applicable one.\n"
        "The output must be one of the following: \n"
        "[공모전] 공학/IT/SW,\n"
        "[공모전] 아이디어/기획,\n"
        "[공모전] 미술/디자인/건축,\n"
        "[공모전] 문학/수기/에세이,\n"
        "[공모전] 기타,\n"
        "교육/특강/프로그램,\n"
        "장학금,\n"
        "서포터즈,\n"
        "봉사활동,\n"
        "취업 정보,\n"
        "해당없음\n\n"
        "Never include any punctuation, quotation marks, or extra text. Only provide the exact category name as the output. The output must be in Korean. Never say anything else."
)
        },
        {"role": "user", "content": user_content}
    ]

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    assistant_content = response.choices[0].message.content

    return assistant_content

def check_title_similarity(new_title, recent_titles):
    system_message = {
        "role": "system",
        "content": ("""
    Determine if the new title is a duplicate of any recent titles. 
    Consider it 중복 if:

    - The title is identical or nearly identical, including minor variations.
    - The title has the same core message, even with different wording or details.

    If the title differs significantly in content or context, output 중복 아님.

    The output should be either 중복 or 중복 아님, with no extra text.
    """)
}


    user_message = {
        "role": "user",
        "content": f"최근 제목들: " + "\n".join(recent_titles) + f"\n새로운 제목: {new_title}"
    }

    messages = [system_message, user_message]

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    assistant_content = response.choices[0].message.content

    return assistant_content
