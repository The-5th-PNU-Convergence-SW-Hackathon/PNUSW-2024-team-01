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
        "If the text contains keywords like '서포터즈', '봉사', '취업', etc., categorize it accordingly.\n"
        "Consider variations in wording and synonyms as matching the relevant category.\n\n"
        "[Competition/Contest] Engineering/Information Technology/Software =([공모전] 공학/IT/SW)\n"
        "[Competition/Contest] Ideas/Planning =([공모전] 아이디어/기획)\n"
        "[Competition/Contest] Art/Design/Architecture =([공모전] 미술/디자인/건축)\n"
        "[Competition/Contest] Literature/Personal Narrative/Essay =([공모전] 문학/수기/에세이)\n"
        "[Competition/Contest] Miscellaneous (for contests not clearly falling into other categories or if uncertain) =([공모전] 기타)\n"
        "Education/Lecture/Program =(교육/특강/프로그램)\n"
        "Scholarship/Scholar (only those awarded, including work-study students) =(장학금)\n"
        "Supporters/Ambassadors =(서포터즈)\n"
        "Volunteer Work =(봉사활동)\n"
        "Employment Information (only company hiring, excluding graduate school, dormitories, etc.) =(취업 정보)\n\n"
        "If the text, based on its context, is related to '대학원', '진학', '연구 조교', '수강 신청', '수강지도', '등록금', '졸업', '논문' or similar topics, categorize it as 'Not Applicable =(해당없음)'.\n\n"
        "If the text contains negative keywords such as '취소', '연기', '변경', or indicates that the event has been canceled or postponed, categorize it as 'Not Applicable =(해당없음)'.\n\n"
        "If the text is too short, unclear, or does not fit into any category, respond with 'Not Applicable =(해당없음)'.\n\n"
        "If the text could fit into multiple categories, prioritize the most relevant category or the first applicable one.\n\n"
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
        "or 해당없음.\n\n"
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
        "content": (
    "Judge whether the following new title is a duplicate of any of the recent titles. "
    "Each input will contain only one announcement title per line. "
    "Recent titles have already been published, and it is crucial to determine whether the new title should be posted. "
    "If the new title is the same or very similar to any of the recent titles, including specific events, names, dates, or locations, output 중복. "
    "Consider minor differences in wording, punctuation, or formatting as duplicates if the main content is the same. "
    "If the new title is semantically or contextually similar to any of the recent titles, even if the wording or phrasing is different, output 중복. "
    "Give additional weight to newer titles when determining similarity, making it more likely to classify a title as 중복 if it closely resembles more recent entries. "
    "Remember, duplicating the same post would cause significant inconvenience to users, so it's essential to avoid posting the same content twice. "
    "The output must be exactly 중복 or 중복 아님, with no additional text or punctuation. Never say anything else.")
    }

    user_message = {
        "role": "user",
        "content": f"새로운 제목: {new_title}\n최근 제목들: " + "\n".join(recent_titles)
    }

    messages = [system_message, user_message]

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    assistant_content = response.choices[0].message.content

    return assistant_content
