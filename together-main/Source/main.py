from gpt_client import answer_gpt
from crawl_announcement import crawl_anns, AnnouncementPages
from selenium_service import WriteNoticeService
from dotenv import load_dotenv
import os


def main():
    load_dotenv()

    anns = crawl_anns(AnnouncementPages.naoe.value)

    announcements = []

    id = os.environ.get("PLATO_ID")
    pw = os.environ.get("PLATO_PW")
    course_name = "[테스트]"

    for ann in anns:
        print("\n\n\n\n")
        # ann.get_content()의 반환값을 문자열로 변환
        ann_content = "\n".join(ann.get_content())
        ann.content = ann_content # answer_gpt(ann_content)
        announcements.append(ann)

    # Write all announcements at once
    WriteNoticeService().write_notices(id, pw, course_name, announcements)


if __name__ == "__main__":
    main()
