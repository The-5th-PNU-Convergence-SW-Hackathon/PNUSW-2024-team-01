from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time
from typing import List
from crawl_announcement import Announcement

class WriteNoticeService:
    def __init__(self):
        # Chrome 옵션 설정
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('headless')
        chrome_options.add_argument("no-sandbox")
        chrome_options.add_argument('window-size=2560x1600')
        chrome_options.add_argument("disable-gpu")
        chrome_options.add_argument("lang=ko_KR")
        chrome_options.add_argument(
            'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36')
        chrome_options.set_capability("goog:loggingPrefs", {"browser": "SEVERE"})  # SEVERE 수준 이상의 로그만 표시

        chrome_driver_path = "C:\\together-main\\Source\\chromedriver-win64\\chromedriver.exe"
        self.driver = webdriver.Chrome(service=Service(chrome_driver_path), options=chrome_options)
        self.driver.get('https://plato.pusan.ac.kr/')

    def write_notices(self, id: str, pw: str, course_name: str, announcements: List[Announcement]):
        self.login(id, pw)
        self.move_to_course(course_name)
        for announcement in announcements:
            if announcement.notice_board_name != "해당없음":
                self.move_to_notice_board(announcement.notice_board_name)
                self.write_notice_in_board(announcement.title, announcement.content_html)
                self.upload_files(announcement.files)

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

    def upload_files(self, files: List[str]):
        for file_path in files:
            self.upload_file(file_path)

    def upload_file(self, file_path: str):
        try:
            # 파일 추가 버튼 클릭 대기 및 클릭
            wait = WebDriverWait(self.driver, 10)
            add_button = wait.until(EC.element_to_be_clickable((By.ID, 'yui_3_17_2_1_1721825930352_861')))
            add_button.click()
            print('파일 추가 버튼 클릭됨.')

            # 파일 입력 요소를 찾을 때까지 대기
            file_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="file"]')))

            # 파일 경로를 절대 경로로 변환
            absolute_path = os.path.abspath(file_path)
            # 파일 경로를 입력하여 파일 선택
            file_input.send_keys(absolute_path)
            print('파일이 성공적으로 선택되었습니다.')

            # 파일 업로드 버튼 클릭
            upload_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.fp-upload-btn.btn-primary.btn')))
            upload_button.click()
            print('파일 업로드 버튼 클릭됨.')

            # 저장 버튼 클릭 (업로드가 완료된 후)
            submit_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="submit"].btn-primary')))
            submit_button.click()
            print('저장 버튼 클릭됨.')

        except Exception as e:
            print(f"파일 업로드 과정에서 오류 발생: {str(e)}")
