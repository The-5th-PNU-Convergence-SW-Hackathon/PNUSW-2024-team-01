from gpt_client import answer_gpt
from crawl_announcement import get_anns_url, crawl_ann_partial, crawl_ann
from selenium_service import WriteNoticeService
from dotenv import load_dotenv
import os
from duplicate_checker import is_recent_title_duplicate, save_title, truncate_text
from page_url_manager import PageUrlManager
import pandas as pd
import gc

# 사전 정의된 키워드와 카테고리 매핑
KEYWORD_CATEGORIES = {
    "장학금": "장학금",
    "장학생": "장학금",
    "지원금": "장학금",
    "인턴": "취업 정보",
    "일자리": "취업 정보",
    "공개모집": "취업 정보",
    "채용": "취업 정보",
    "공채": "취업 정보",
    "현장실습": "취업 정보"
}

# 제외할 키워드
EXCLUDE_KEYWORDS = ["대출", "재입학", "진학", "조교", "수강 신청", "수강신청", "수강 지도", "수강지도", "취소", "연기", "변경"]

def categorize_by_keywords(title, content_text):
    """
    제목과 내용에서 키워드를 검색하여 게시판을 직접 분류
    키워드가 매핑된 카테고리가 있는 경우 해당 카테고리로 분류하고, 그렇지 않으면 None 반환
    """
    for keyword in EXCLUDE_KEYWORDS:
        if keyword in title + content_text:
            return "해당없음"  # 제외할 키워드가 포함된 경우 '해당없음'으로 바로 반환

    for keyword, category in KEYWORD_CATEGORIES.items():
        if keyword in title:
            return category

    return None

def categorize_announcement(title, content_text):
    # 먼저 키워드를 기반으로 카테고리 분류 시도
    category = categorize_by_keywords(title, content_text)

    if category:
        return category
    else:
        # 사전 정의된 키워드로 분류되지 않으면 ChatGPT를 통해 카테고리 분류
        combined_text = f"{title}\n{content_text}"
        truncated_content = truncate_text(combined_text, 1000)  # 토큰 수 제한(1000토큰 = 약 500자)
        return answer_gpt(truncated_content)

def update_csv_with_announcement_numbers(updates, filename='C:\\together-main\\Source\\pages.csv'):
    df = pd.read_csv(filename)

    # 각 URL에 대한 공지 번호 업데이트
    for page_url, announcement_number in updates.items():
        df.loc[df['page_url'] == page_url, 'number'] = announcement_number

    # CSV 파일 다시 쓰기
    df['number'] = df['number'].fillna(0).astype(int)
    df.to_csv(filename, index=False)

def main():
    load_dotenv()
    page_url_manager = PageUrlManager()
    announcements = []
    updates = {}  # 업데이트할 URL과 공지 번호 저장

    # course_name을 course_url로 변환하거나 직접 course_url을 사용
    course_url = "https://plato.pusan.ac.kr/course/view.php?id=157301"  # 실제 course_url 사용

    for announcement_page in page_url_manager.announcement_pages:
        ann_urls, latest_announcement_number = get_anns_url(announcement_page)  # 각 페이지에서 공지사항 URL 가져오기
        for url in ann_urls:

            # 메모리 누수를 방지하기 위해 주기적으로 가비지 컬렉션 실행
            gc.collect()

            # 제목만 부분적으로 크롤링
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
                print(f"카테고리 분류 결과: {category} - {partial_ann.title}")

                if category in [
                    "[공모전] 공학/IT/SW",
                    "[공모전] 아이디어/기획",
                    "[공모전] 미술/디자인/건축",
                    "[공모전] 문학/수기/에세이",
                    "[공모전] 기타",
                    "교육/특강/프로그램",
                    "장학금",
                    "서포터즈",
                    "봉사활동",
                    "취업 정보"
                ]:
                    # 전체 공지사항 크롤링
                    full_ann = crawl_ann(url)
                    full_ann.notice_board_name = category  # 게시판 이름 업데이트
                    announcements.append(full_ann)
                    save_title(partial_ann.title)  # 제목 저장

                    # 주기적으로 파일 핸들을 관리하기 위해 파일 닫기
                    with open('log.txt', 'a') as log_file:
                        log_file.write(f"Saved announcement: {full_ann.title}\n")

                    WriteNoticeService().write_notices(course_url, [full_ann])  # 공지사항 작성
                    print(f"게시글 작성 완료\n")
                else:
                    print("")

        # URL의 최신 공지 번호를 업데이트 딕셔너리에 저장
        if latest_announcement_number > announcement_page.number:
            updates[announcement_page.page_url] = latest_announcement_number
            update_csv_with_announcement_numbers(updates)
            updates = {}

if __name__ == "__main__":
    main()
