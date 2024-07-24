import openai
import os

def answer_gpt(user_content):
    openai.api_key = os.environ.get('GPT_API_KEY')

    messages = [
        {"role": "system", "content": (
            "다음 글을 적절한 카테고리로 분류해서 그 카테고리만 말해. 만약 내용에 대회나 공모전이 있다면 무조건 공모전 중 하나로 분류해.\n\n"
            "[공모전] 공학/IT/SW\n"
            "[공모전] 아이디어/기획\n"
            "[공모전] 미술/디자인/건축\n"
            "[공모전] 사진/영상/UCC\n"
            "[공모전] 문학/수기/에세이\n"
            "[공모전] 기타\n"
            "교육/특강/프로그램\n"
            "장학금\n"
            "서포터즈\n"
            "봉사활동\n"
            "취업 정보\n"
            "그 외 해당되지 않는다면 '해당없음'으로 응답해줘. \n\n"
            "장학금, 서포터즈, 봉사, 취업 등 위 게시판의 키워드들과 하나라도 겹치면 그걸로 판단해.\n"
            "다른 추가적인 내용은 절대 붙이지 말고 분류한 카테고리 혹은 '해당없음'으로만 출력해.\n"
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

    # 시스템 메시지 정의
    system_message = {
        "role": "system",
        "content": (
            "다음 새로운 제목과 최근 제목들 중에 중복된 제목이 있는지 판단해줘. 똑같으면 '중복'을, 똑같지 않으면 '중복 아님'을 출력해."
        )
    }

    # 사용자 메시지 정의
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
