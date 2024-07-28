import os
from dotenv import load_dotenv
from selenium_service import WriteNoticeService
from crawl_announcement import get_recent_anns_from_rss, crawl_ann, Announcement
from gpt_client import answer_gpt
from duplicate_checker import is_recent_title_duplicate, save_title, truncate_text
from datetime import datetime

def   main():
    load_dotenv()
    id = os.environ.get("PLATO_ID")
    pw = os.environ.get("PLATO_PW")
    course_name = "[테스트]"
    rss_url = "https://biz.pusan.ac.kr/bbs/biz/2557/rssList.do?row=50"

    recent_urls = get_recent_anns_from_rss(rss_url)

    for url in reversed(recent_urls):  # 최신 글을 먼저 처리하기 위해 리스트를 역순으로
        ann = crawl_ann(url)
        if ann:
            duplicate_check = is_recent_title_duplicate(ann.title)
            print(f"중복 체크 결과: {duplicate_check} - {ann.title}")  # 중복 체크 결과 출력
            if duplicate_check == "중복":
                print(f"중복된 제목: {ann.title}\n")
                continue

            combined_text = f"{ann.title}\n\n{ann.content_text}"
            truncated_content = truncate_text(combined_text, 15000)  # 토큰 수 제한
            # print(f"자른 후 텍스트 내용: {truncated_content[:500]}...")  # 디버깅 메시지 (첫 500자)

            category = answer_gpt(truncated_content)
            print(f"챗GPT 응답: {category} - {ann.title}")  # 카테고리 출력
            if category in [
                "[공모전] 공학/IT/SW",
                "[공모전] 아이디어/기획",
                "[공모전] 미술/디자인/건축",
                "[공모전] 사진/영상/UCC",
                "[공모전] 문학/수기/에세이",
                "[공모전] 기타",
                "교육/특강/프로그램",
                "장학금",
                "서포터즈",
                "봉사활동",
                "취업 정보"
            ]:
                ann.notice_board_name = category  # 게시판 이름을 업데이트
                WriteNoticeService().write_notices(id, pw, course_name, [ann])
                save_title(ann.title)
                print(f"게시글 작성 완료\n")
            else:
                print(f"해당 카테고리 없음\n")  # 카테고리 없음

if __name__ == "__main__":
    main()
