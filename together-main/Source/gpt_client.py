import openai
import os

def answer_gpt(user_content):
    openai.api_key = os.environ.get('GPT_API_KEY')

    messages = [
        {"role": "system", "content": (
            "Categorize the following text into the appropriate category and only state the category.\n"
            "If the text contains keywords like '대회' or '공모전' categorize it under one of the [Competition/Contest] categories\n"
            "If it matches any of the keywords from the above categories such as 장학,서포터즈,봉사,취업,etc., categorize it accordingly.\n\n"
            "[Competition/Contest] Engineering/Information Technology/Software =([공모전] 공학/IT/SW)\n"
            "[Competition/Contest] Ideas/Planning =([공모전] 아이디어/기획)\n"
            "[Competition/Contest] Art/Design/Architecture =([공모전] 미술/디자인/건축)\n"
            "[Competition/Contest] Photography/Video/User Created Content =([공모전] 사진/영상/UCC)\n"
            "[Competition/Contest] Literature/Personal Narrative/Essay =([공모전] 문학/수기/에세이)\n"
            "[Competition/Contest] Miscellaneous (for contests not clearly falling into other categories) =([공모전] 기타)\n"
            "Education/Lecture/Program =(교육/특강/프로그램)\n"
            "Scholarship/Scholar(only those awarded, including work-study students) =(장학금)\n"
            "Supporters/Ambassadors =(서포터즈)\n"
            "Volunteer Work =(봉사활동)\n"
            "Employment Information (only company hiring, excluding graduate school, dormitories, etc.) =(취업 정보)\n"
            "If it does not fall under any category, respond with 'Not Applicable =(해당없음)'.\n\n"
            "The output must be one of the following: [공모전] 공학/IT/SW,\n"
            "[공모전] 아이디어/기획,\n"
            "[공모전] 미술/디자인/건축,\n"
            "[공모전] 사진/영상/UCC,\n"
            "[공모전] 문학/수기/에세이,\n"
            "[공모전] 기타,\n"
            "교육/특강/프로그램,\n"
            "장학금,\n"
            "서포터즈,\n"
            "봉사활동,\n"
            "취업 정보,\n"
            "or 해당없음. Do not change or add to the text. The output must be in Korean.\n"
            "Do not use quotation marks. Never say anything else."
        )},
        {"role": "user", "content": user_content}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    assistant_content = response['choices'][0]['message']['content'].strip()

    return assistant_content


def check_title_similarity(new_title, recent_titles):
    openai.api_key = os.environ.get('GPT_API_KEY')

    system_message = {
        "role": "system",
        "content": (
            "Judge whether the following new title is a duplicate of any of the recent titles. If it's the same, output 중복\n"
            "Even if the content is the same, the first 2-3 characters of the new title might be different.\n"
            "In other words, even if the titles are not exactly the same, if you determine the content is the same, output 중복.\n"
            "If it's not the same, output 중복 아님. Do not say anything other than these two responses.\n"
            "The output must be in Korean. Do not use quotation marks. Never say anything else."
        )
    }

    user_message = {
        "role": "user",
        "content": f"새로운 제목: {new_title}\n최근 제목들: " + "\n".join(recent_titles)
    }

    messages = [system_message, user_message]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    assistant_content = response['choices'][0]['message']['content'].strip()

    print(f"GPT 응답: {assistant_content}")  # 응답 로그 출력

    return assistant_content
