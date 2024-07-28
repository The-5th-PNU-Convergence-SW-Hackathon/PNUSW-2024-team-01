import os
from datetime import datetime, timedelta
import tiktoken
from gpt_client import check_title_similarity

def truncate_text(text, max_tokens):
    encoding = tiktoken.get_encoding("cl100k_base")

    # 텍스트를 토큰으로 인코딩
    tokens = encoding.encode(text)
    # print(f"총 토큰 수: {len(tokens)}")  # 디버깅 메시지

    # 최대 토큰 수로 자르기
    truncated_tokens = tokens[:max_tokens]
    # print(f"자른 후 토큰 수: {len(truncated_tokens)}")  # 디버깅 메시지

    # 토큰을 다시 텍스트로 디코딩
    truncated_text = encoding.decode(truncated_tokens)
    # print(f"자른 후 텍스트 길이: {len(truncated_text)}")  # 디버깅 메시지

    return truncated_text


def is_recent_title_duplicate(new_title, filename='titles.txt'):
    recent_titles = []
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            for line in lines:
                saved_date, saved_title = line.strip().split('|')
                saved_date = datetime.strptime(saved_date, '%Y-%m-%d')
                if saved_date > datetime.now() - timedelta(days=7):
                    recent_titles.append(saved_title)

    # 새 제목과 최근 제목들로 구성된 전체 텍스트 생성
    combined_text = new_title + "\n" + "\n".join(recent_titles)

    # 최대 토큰 수를 초과할 경우 최신 제목부터 자르기
    encoding = tiktoken.get_encoding("cl100k_base")
    while len(encoding.encode(combined_text)) > 15000:
        recent_titles.pop(0)  # 가장 오래된 제목 제거
        combined_text = new_title + "\n" + "\n".join(recent_titles)
    # print(recent_titles)
    return check_title_similarity(new_title, recent_titles)


def save_title(title, filename='titles.txt'):
    with open(filename, 'a', encoding='utf-8') as file:
        file.write(f"{datetime.now().strftime('%Y-%m-%d')}|{title}\n")
