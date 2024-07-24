from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from typing import List
from crawl_announcement import Announcement

class WriteNoticeService:
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument("no-sandbox")
        options.add_argument('window-size=2560x1600')
        options.add_argument("disable-gpu")
        options.add_argument("lang=ko_KR")
        options.add_argument(
            'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36')

        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.driver.get('https://plato.pusan.ac.kr/')

    def write_notices(self, id: str, pw: str, course_name: str, announcements: List[Announcement]):
        self.login(id, pw)
        self.move_to_course(course_name)
        for announcement in announcements:
            if announcement.notice_board_name != "해당없음":
                self.move_to_notice_board(announcement.notice_board_name)
                self.write_notice_in_board(announcement.title, announcement.content)

    def login(self, id: str, pw: str):
        username_input = self.driver.find_element(By.ID, 'input-username')
        username_input.send_keys(id)

        password_input = self.driver.find_element(By.ID, "input-password")
        password_input.send_keys(pw)

        submit = self.driver.find_element(By.NAME, "loginbutton")
        submit.click()
        # print("로그인 성공")

    def move_to_course(self, course_name: str):
        course_link = self.driver.find_element(By.XPATH, f'//h3[text()="{course_name}"]/ancestor::a')
        course_link.click()
        # print("강좌 이동 완료")

    def move_to_notice_board(self, notice_board_name: str):
        try:
            notice_board_link = self.driver.find_element(By.XPATH, '//a[contains(span[@class="instancename"], "' + notice_board_name + '")]')
            notice_board_link.click()
            # print("게시판 이동 완료")
        except Exception as e:
            print(f"게시판을 찾을 수 없습니다: {notice_board_name}, 오류: {str(e)}")

    def write_notice_in_board(self, subject: str, content: str):
        write_button = self.driver.find_element(By.XPATH, '//a[contains(text(), "쓰기")]')
        write_button.click()
        # print("쓰기 버튼 클릭 완료")

        input_subject = self.driver.find_element(By.NAME, "subject")
        input_subject.send_keys(subject)
        # print("제목 입력 완료")

        input_content = self.driver.find_element(By.ID, "id_contenteditable")
        self.driver.execute_script("arguments[0].innerHTML = arguments[1];", input_content, content)
        # print("내용 입력 완료")
        input_content.click()
        # print("입력창 클릭 완료")

        submit_button = self.driver.find_element(By.NAME, "submitbutton")
        submit_button.click()
        # print("게시글 작성 완료")
