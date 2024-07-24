import openai
import os

def answer_gpt(user_content):
    openai.api_key = os.environ.get('GPT_API_KEY')

    messages = [
        {"role": "system", "content": (
            "다음 글을 적절한 카테고리로 분류해서 그 카테고리만 말해.:\n\n"
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
            "다른 추가적인 내용은 절대!!!!!!!!!!!!!!!!!!!! 붙이지 말고 '카테고리' 혹은 '해당없음'으로만 출력해."
        )},
        {"role": "user", "content": user_content}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    assistant_content = response['choices'][0]['message']['content'].strip()

    return assistant_content
