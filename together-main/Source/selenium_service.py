from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from typing import List
from crawl_announcement import Announcement
from bs4 import BeautifulSoup

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

        chrome_driver_path = "C:\\together-main\\Source\\chromedriver-win64\\chromedriver.exe"
        self.driver = webdriver.Chrome(service=Service(chrome_driver_path), options=chrome_options)
        self.driver.get('https://plato.pusan.ac.kr/')

    def write_notices(self, id: str, pw: str, course_name: str, announcements: List[Announcement]):
        self.login(id, pw)
        self.move_to_course(course_name)
        for announcement in announcements:
            if announcement.notice_board_name != "해당없음":
                self.move_to_notice_board(announcement.notice_board_name)
                self.write_notice_in_board(announcement.title, announcement.content_html, announcement.files)

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
        notice_board_link = self.driver.find_element(By.XPATH, '//a[contains(span[@class="instancename"], "' + notice_board_name + '")]')
        notice_board_link.click()

    def write_notice_in_board(self, subject: str, content: str, files: List[str]):
        write_button = self.driver.find_element(By.XPATH, '//a[contains(text(), "쓰기")]')
        write_button.click()

        input_subject = self.driver.find_element(By.NAME, "subject")
        input_subject.send_keys(subject)

        input_content = self.driver.find_element(By.ID, "id_contenteditable")

        # BeautifulSoup을 사용하여 이미지 태그에 클래스 추가
        soup = BeautifulSoup(content, 'html.parser')
        images = soup.find_all('img')
        for img in images:
            img['class'] = img.get('class', []) + ['img-responsive', 'atto_image_button_text-bottom']

        content_with_styles = str(soup)

        self.driver.execute_script("arguments[0].innerHTML = arguments[1];", input_content, content_with_styles)
        input_content.click()

        # 파일 업로드 수행
        self.upload_files(files)

        # 저장 버튼 클릭
        self.click_with_js('input[type="submit"].btn-primary')

    def upload_files(self, files: List[str]):
        for file_path in files:
            self.upload_file(file_path)

    def upload_file(self, file_path: str):
        # 첨부파일 요소 찾기 및 클릭
        self.click_with_js('a[role="button"][title="추가 ..."].btn.btn-default.btn-sm')

        # 파일 선택 요소 찾기
        file_input = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="file"]'))
        )

        # 파일 경로를 절대 경로로 변환
        absolute_path = os.path.abspath(file_path)

        # 파일 경로를 입력하여 파일 선택
        file_input.send_keys(absolute_path)

        # 파일 업로드 버튼 클릭
        self.click_with_js('button.fp-upload-btn.btn-primary.btn')

    def click_with_js(self, css_selector: str):
        element = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, css_selector))
        )
        self.driver.execute_script("arguments[0].click();", element)
