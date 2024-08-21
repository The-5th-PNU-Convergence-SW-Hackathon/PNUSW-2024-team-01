import os
from datetime import datetime, timedelta
import tiktoken
from gpt_client import check_title_similarity
from difflib import SequenceMatcher

def truncate_text(text, max_tokens):
    encoding = tiktoken.get_encoding("cl100k_base")

    # 텍스트를 토큰으로 인코딩
    tokens = encoding.encode(text)

    # 최대 토큰 수로 자르기
    truncated_tokens = tokens[:max_tokens]

    # 토큰을 다시 텍스트로 디코딩
    truncated_text = encoding.decode(truncated_tokens)

    return truncated_text

def calculate_similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

def is_recent_title_duplicate(new_title, filename='titles.txt'):
    recent_titles = []
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            for line in lines:
                saved_date, saved_title = line.strip().split('$')
                saved_date = datetime.strptime(saved_date, '%Y-%m-%d')
                if saved_date > datetime.now() - timedelta(days=7):
                    recent_titles.append((saved_date, saved_title))

    # 최신 제목들을 날짜 기준으로 정렬하고 1000개 이하로 자르기
    recent_titles.sort(reverse=True, key=lambda x: x[0])  # 최신순으로 정렬
    recent_titles = [title for _, title in recent_titles[:1000]]  # 1000개 이하로 자름

    # 원시적인 텍스트 유사도 검사 (80% 이상이면 중복으로 간주)
    for title in recent_titles:
        if calculate_similarity(new_title, title) >= 0.8:
            return '중복'

    # GPT를 사용해 중복 여부 판단
    return check_title_similarity(new_title, recent_titles)

def save_title(title, filename='titles.txt'):
    with open(filename, 'a', encoding='utf-8') as file:
        file.write(f"{datetime.now().strftime('%Y-%m-%d')}${title}\n")
