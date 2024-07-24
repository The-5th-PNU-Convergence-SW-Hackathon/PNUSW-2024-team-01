from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
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
            'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36')

        # 명시적으로 경로 설정
        chrome_driver_path = "C:\\together-main\\Source\\chromedriver-win64\\chromedriver.exe"
        self.driver = webdriver.Chrome(service=Service(chrome_driver_path), options=options)
        self.driver.get('https://plato.pusan.ac.kr/')

    def write_notices(self, id: str, pw: str, course_name: str, announcements: List[Announcement]):
        self.login(id, pw)
        self.move_to_course(course_name)
        for announcement in announcements:
            if announcement.notice_board_name != "해당없음":
                self.move_to_notice_board(announcement.notice_board_name)
                self.write_notice_in_board(announcement.title, announcement.content_html)

    def login(self, id: str, pw: str):
        username_input = self.driver.find_element(By.ID, 'input-username')
        username_input.send_keys(id)

        password_input = self.driver.find_element(By.ID, "input-password")
        password_input.send_keys(pw)

        submit = self.driver.find_element(By.NAME, "loginbutton")
        submit.click()

    def move_to_course(self, course_name: str):
        course_link = self.driver.find_element(By.XPATH, f'//h3[text()="{course_name}"]/ancestor::a')
        course_link.click()

    def move_to_notice_board(self, notice_board_name: str):
        try:
            notice_board_link = self.driver.find_element(By.XPATH, '//a[contains(span[@class="instancename"], "' + notice_board_name + '")]')
            notice_board_link.click()
        except Exception as e:
            print(f"게시판을 찾을 수 없습니다: {notice_board_name}, 오류: {str(e)}")

    def write_notice_in_board(self, subject: str, content: str):
        write_button = self.driver.find_element(By.XPATH, '//a[contains(text(), "쓰기")]')
        write_button.click()

        input_subject = self.driver.find_element(By.NAME, "subject")
        input_subject.send_keys(subject)

        input_content = self.driver.find_element(By.ID, "id_contenteditable")
        self.driver.execute_script("arguments[0].innerHTML = arguments[1];", input_content, content)
        input_content.click()

        submit_button = self.driver.find_element(By.NAME, "submitbutton")
        submit_button.click()
