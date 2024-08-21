from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from typing import List
from crawl_announcement import Announcement
from bs4 import BeautifulSoup
from dotenv import load_dotenv


class WriteNoticeService:
    def __init__(self):
        load_dotenv()
        window_size = os.getenv('WINDOW_SIZE')
        user_agent = os.getenv('USER_AGENT')
        chrome_driver_path = os.getenv('CHROME_DRIVER_PATH')

        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('no-sandbox')
        options.add_argument(f'window-size={window_size}')
        options.add_argument('disable-gpu')
        options.add_argument('lang=ko_KR')
        options.add_argument(f'user-agent={user_agent}')

        driver_service = Service(chrome_driver_path)
        self.driver = webdriver.Chrome(service=driver_service, options=options)
        self.driver.get('https://plato.pusan.ac.kr/')

        # 로그인 수행
        self.login(os.getenv("PLATO_ID"), os.getenv("PLATO_PW"))

    def login(self, id: str, pw: str):
        username_input = self.driver.find_element(By.ID, 'input-username')
        username_input.send_keys(id)

        password_input = self.driver.find_element(By.ID, "input-password")
        password_input.send_keys(pw)

        submit = self.driver.find_element(By.NAME, "loginbutton")
        submit.click()

    def move_to_course(self, course_url: str):
        self.driver.get(course_url)

    def move_to_notice_board(self, notice_board_name: str):
        notice_board_link = self.driver.find_element(By.XPATH,
                                                     f'//a[span[contains(@class, "instancename") and contains(text(), "{notice_board_name}")]]')
        notice_board_link.click()

    def write_notices(self, course_url: str, announcements: List[Announcement]):
        self.move_to_course(course_url)

        for announcement in announcements:
            if announcement.notice_board_name != "해당없음":
                self.move_to_notice_board(announcement.notice_board_name)
                self.write_notice_in_board(announcement.title, announcement.url, announcement.content_html, announcement.files)

                # 공지 작성 후 코스 페이지로 돌아가기
                self.move_to_course(course_url)

    def write_notice_in_board(self, subject: str, url: str, content: str, files: List[str]):
        write_button = self.driver.find_element(By.XPATH, '//a[contains(text(), "쓰기")]')
        write_button.click()

        input_subject = self.driver.find_element(By.NAME, "subject")
        input_subject.send_keys(subject)

        input_content = self.driver.find_element(By.ID, "id_contenteditable")

        # 본문 최상단에 공지사항 링크 추가
        content_with_link = f'<p>본문 링크 : <a href="{url}">{url}</a></p>' + content

        # BeautifulSoup을 사용하여 이미지 태그에 클래스 추가
        soup = BeautifulSoup(content_with_link, 'html.parser')
        images = soup.find_all('img')
        for img in images:
            img['class'] = img.get('class', []) + ['img-responsive', 'atto_image_button_text-bottom']

        content_with_styles = str(soup)

        # Selenium을 통해 내용을 입력 (입력 이벤트 강제 트리거)
        self.driver.execute_script("""
            arguments[0].innerHTML = arguments[1];
            arguments[0].focus();
            arguments[0].dispatchEvent(new Event('focus', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('blur', { bubbles: true }));
            arguments[0].blur();
        """, input_content, content_with_styles)

        # 파일 업로드 수행
        if files:
            self.upload_files(files)
            try:
                # 파일 선택 요소 찾기
                file_input = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="file"]'))
                )
            except:
                # 파일 선택 요소를 찾지 못하면 저장 버튼 클릭 (업로드 대기)
                self.click_with_js('input[type="submit"].btn-primary')
        else:
            # 파일이 없으면 바로 저장 버튼 클릭
            self.click_with_js('input[type="submit"].btn-primary')

    def upload_files(self, files: List[str]):
        for file_path in files:
            self.upload_file(file_path)

    def upload_file(self, file_path: str):
        # 첨부파일 요소 찾기 및 클릭
        self.click_with_js('a[role="button"][title="추가 ..."].btn.btn-default.btn-sm')

        # 파일 선택 요소 찾기
        file_input = WebDriverWait(self.driver, 10).until(
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
