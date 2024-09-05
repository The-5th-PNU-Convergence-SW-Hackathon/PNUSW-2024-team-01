from gpt_client import answer_gpt
from crawl_announcement import get_anns_url, crawl_ann_partial, crawl_ann
from selenium_service import WriteNoticeService
from duplicate_checker import is_recent_title_duplicate, save_title, truncate_text
from page_url_manager import PageUrlManager
import json
import pandas as pd
import gc
import os
from datetime import datetime

# JSON 파일 불러오기
with open('env.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# JSON 데이터를 변수로 할당
KEYWORD_CATEGORIES = config['KEYWORD_CATEGORIES']
EXCLUDE_KEYWORDS = config['EXCLUDE_KEYWORDS']
CATEGORIES = config['CATEGORIES']
def categorize_by_keywords(title, content_text):
    # 제목과 내용에서 키워드를 검색하여 게시판을 직접 분류. 매핑된 카테고리가 있는 경우 해당 카테고리로 분류, 아니면 None 반환
    for keyword, category in KEYWORD_CATEGORIES.items():
        if keyword in title:  # + content_text
            return category

    for keyword in EXCLUDE_KEYWORDS:
        if keyword in title + content_text:
            return "해당없음"
    return None

def categorize_announcement(title, content_text):
    # 먼저 키워드를 기반으로 카테고리 분류 시도
    category = categorize_by_keywords(title, content_text)
    if category:
        return category
    else:
        # 사전 정의된 키워드로 분류되지 않으면 ChatGPT를 통해 카테고리 분류
        combined_text = f"{title}\n{content_text}"
        truncated_content = truncate_text(combined_text, 1000)  # 토큰 수 제한(1000토큰 = 약 500~700글자)
        return answer_gpt(truncated_content)

def update_csv_with_announcement_numbers(updates, filename: str):
    df = pd.read_csv(f'{filename}')

    # 각 URL에 대한 공지 번호 업데이트
    for page_url, announcement_number in updates.items():
        df.loc[df['page_url'] == page_url, 'number'] = announcement_number

    # CSV 파일 다시 쓰기
    df['number'] = df['number'].fillna(0).astype(int)
    df.to_csv(filename, index=False)

def main():
    today_date = datetime.now().strftime("%Y-%m-%d") # 오늘 날짜 가져오기
    page_url_manager = PageUrlManager()
    announcements = []
    updates = {}  # 업데이트할 URL과 공지 번호 저장
    writenoticeService = WriteNoticeService()
    course_url = "https://plato.pusan.ac.kr/course/view.php?id=157301"  # 실제 course_url 사용

    for announcement_page in page_url_manager.announcement_pages:
        ann_urls, latest_announcement_number = get_anns_url(announcement_page)  # 각 페이지에서 공지사항 URL 가져오기
        for url in ann_urls:

            # 메모리 누수를 방지하기 위해 주기적으로 가비지 컬렉션 실행
            gc.collect()

            # 제목+내용만 부분적으로 크롤링
            partial_ann = crawl_ann_partial(url)
            if partial_ann:
                # 제목 중복 체크
                duplicate_check = is_recent_title_duplicate(partial_ann.title)
                print(f"중복 체크 결과: {duplicate_check} - {partial_ann.title}")
                if duplicate_check == "중복":
                    print("")
                    continue

                # 키워드 기반 카테고리 분류 시도
                category = categorize_announcement(partial_ann.title, partial_ann.content_text)
                print(f"카테고리 분류 결과: {category}")

                if category in CATEGORIES:
                    # 전체 공지사항 크롤링
                    full_ann = crawl_ann(url)
                    full_ann.notice_board_name = category  # 게시판 이름 업데이트
                    announcements.append(full_ann)
                    save_title(partial_ann.title)  # 제목 저장

                    writenoticeService.write_notices(course_url, [full_ann])  # 공지사항 작성
                    print(f"게시글 작성 완료\n")
                else:
                    print("")

        # URL의 최신 공지 번호를 업데이트 딕셔너리에 저장
        if latest_announcement_number > announcement_page.number:
            updates[announcement_page.page_url] = latest_announcement_number
            update_csv_with_announcement_numbers(updates, os.getenv('PAGE_NAME'))
            updates = {}

    # 공지글 체크 해제 및 별 제거 작업 시작 알림
    print("공지글 수정 작업을 시작합니다.")

    # 오늘 올린 공지가 아닌 모든 게시글의 공지글 체크 해제 및 별 제거
    writenoticeService.remove_stars_and_uncheck_notices(course_url, today_date)

def main_specific(url, course_url):
    announcements = []
    writenoticeService = WriteNoticeService()

    # 메모리 누수를 방지하기 위해 주기적으로 가비지 컬렉션 실행
    gc.collect()

    # 제목+내용만 부분적으로 크롤링
    partial_ann = crawl_ann_partial(url)
    if partial_ann:
        # 제목 중복 체크
        duplicate_check = is_recent_title_duplicate(partial_ann.title)
        print(f"중복 체크 결과: {duplicate_check} - {partial_ann.title}")
        if duplicate_check == "중복":
            print("")
            return

        # 키워드 기반 카테고리 분류 시도
        category = categorize_announcement(partial_ann.title, partial_ann.content_text)
        print(f"카테고리 분류 결과: {category}")

        if category in CATEGORIES:
            # 전체 공지사항 크롤링
            full_ann = crawl_ann(url)
            full_ann.notice_board_name = category  # 게시판 이름 업데이트
            announcements.append(full_ann)
            save_title(partial_ann.title)  # 제목 저장

            writenoticeService.write_notices(course_url, [full_ann])  # 공지사항 작성
            print(f"게시글 작성 완료\n")
        else:
            print("")
    else:
        print("공지사항 크롤링에 실패했습니다.")

if __name__ == "__main__":
    use_specific = False  # False로 변경하면 main() 함수가 실행됨

    if use_specific:
        url = input("URL을 입력하세요: ")
        course_url = "https://plato.pusan.ac.kr/course/view.php?id=157301"
        main_specific(url, course_url)
    else:
        main()

