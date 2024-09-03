from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from typing import List
from crawl_announcement import Announcement
from dotenv import load_dotenv
from bs4 import BeautifulSoup

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
        self.login(os.getenv('PLATO_ID'), os.getenv('PLATO_PW'))

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
                self.write_notice_in_board(announcement.title, announcement.url, announcement.content_html,
                                           announcement.files, announcement.notice_board_name)

                # 공지 작성 후 코스 페이지로 돌아가기
                self.move_to_course(course_url)

    def write_notice_in_board(self, subject: str, url: str, content: str, files: List[str], notice_board_name: str):
        # "장학금" 게시판에서는 제목에 별을 추가하지 않음
        if notice_board_name != "장학금":
            # 제목 맨 앞에 ⭐ 추가
            subject = f"⭐ {subject}"

        # '쓰기' 버튼을 찾고 화면에 나타날 때까지 스크롤 (공지글이 많으면 버튼이 밀림)
        write_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//a[contains(text(), "쓰기")]'))
        )

        # 스크롤하여 요소가 보이도록 함
        self.driver.execute_script("arguments[0].scrollIntoView(true);", write_button)
        write_button.click()

        # 제목 입력
        input_subject = self.driver.find_element(By.NAME, "subject")
        input_subject.send_keys(subject)

        # 본문 입력
        input_content = self.driver.find_element(By.ID, "id_contenteditable")

        # 본문 최상단에 공지사항 링크 추가
        content_with_link = f'<p>본문 링크 : <a href="{url}">{url}</a></p>' + content

        # BeautifulSoup을 사용하여 이미지 태그에 클래스 추가 (화면 맞춤)
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

        # "장학금" 게시판이 아닌 경우에만 공지 글로 설정 (체크박스 클릭)
        if notice_board_name != "장학금":
            notice_checkbox = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "id_notice"))
            )
            if not notice_checkbox.is_selected():
                notice_checkbox.click()

        # 파일 업로드 수행
        if files:
            self.upload_files(files)
            try:
                # 파일 선택 요소 찾기
                file_input = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="file"]'))
                )
            except:
                # 파일 선택 요소를 찾지 못하면 저장 버튼 클릭 (업로드 시간 대기 용)
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

    def remove_stars_and_uncheck_notices(self, course_url: str, today_date: str):
        # 체크할 게시판 리스트
        board_names = [
            "교육/특강/프로그램", "[공모전] 공학/IT/SW", "[공모전] 아이디어/기획",
            "[공모전] 미술/디자인/건축", "[공모전] 문학/수기/에세이", "[공모전] 기타",
            "봉사활동", "서포터즈", "취업 정보"
        ]

        for board_name in board_names:
            self.move_to_course(course_url)
            self.move_to_notice_board(board_name)
            print(f"현재 작업 중인 게시판: {board_name}")

            while True:
                try:
                    # 공지글 아이콘이 있는지 확인
                    notice_icon = self.driver.find_element(By.CSS_SELECTOR, "img[alt='공지글']")
                except Exception:
                    print(f"게시판 {board_name}에 공지글이 없습니다. 다음 게시판으로 이동합니다.\n")
                    break  # 이 게시판을 종료하고 다음 게시판으로 이동

                try:
                    # 마지막 행(row) 요소 가져오기
                    rows = self.driver.find_elements(By.CSS_SELECTOR, "tr")

                    last_row = rows[-2]

                    try:
                        # 제목 추출 (child 3)
                        title_element = last_row.find_element(By.CSS_SELECTOR, "td:nth-child(3) a")
                        notice_url = title_element.get_attribute("href")
                        date_selector = "td:nth-child(5)"  # 날짜 선택자 기본값
                    except Exception:
                        # child 3에서 찾지 못하면 child 4에서 시도
                        title_element = last_row.find_element(By.CSS_SELECTOR, "td:nth-child(4) a")
                        notice_url = title_element.get_attribute("href")
                        date_selector = "td:nth-child(6)"  # child 4에서 찾았을 경우 날짜 선택자 변경

                    title_text = title_element.text.strip()

                    # 제목에 별이 없는 경우 다음 게시글로 이동
                    if not title_text.startswith("⭐"):
                        # 해당 row 제거 후 다시 시도
                        self.driver.execute_script("arguments[0].remove();", last_row)
                        continue  # 다음 게시글로 이동

                    # 날짜 추출
                    date_element = last_row.find_element(By.CSS_SELECTOR, date_selector)
                    date_text = date_element.text.strip()

                    # 오늘 날짜의 게시글이면 다음 게시판으로 이동
                    if date_text == today_date:
                        print(f"{board_name} 게시판의 모든 게시글이 처리되었습니다.\n")
                        break  # 이 게시판을 종료하고 다음 게시판으로 이동

                    # 오늘 날짜가 아니면 공지 체크 해제 및 제목에서 ⭐ 제거
                    new_title = title_text[1:].strip()

                    # 공지글 URL로 접속
                    self.driver.get(notice_url)

                    # 수정 버튼 찾기
                    modify_button = self.driver.find_element(By.XPATH, "//a[contains(@class, 'modify')]")
                    modify_link = modify_button.get_attribute("href")
                    modify_link = modify_link.replace("&amp;", "&")

                    # 수정 페이지로 이동
                    self.driver.get(modify_link)

                    # 체크박스 해제 및 제목 수정
                    self.uncheck_notice_and_update_title(new_title)
                    print(f"수정 완료: {new_title}")

                except Exception as e:
                    # 해당 row 제거 후 다시 시도
                    self.driver.execute_script("arguments[0].remove();", last_row)
                    continue  # 에러가 발생하면 해당 게시글을 건너뛰고 다음 게시글로 이동

    def uncheck_notice_and_update_title(self, new_title: str):
        # 공지 체크박스 찾기
        notice_checkbox = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "id_notice"))
        )
        if notice_checkbox.is_selected():
            notice_checkbox.click()

        # 제목 수정
        input_subject = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.NAME, "subject"))
        )
        input_subject.clear()
        input_subject.send_keys(new_title)

        # 변경사항 저장
        self.click_with_js('input[type="submit"].btn-primary')

        # 변경사항 저장 후, 해당 게시판으로 다시 이동
        self.navigate_to_board(new_title)

    def navigate_to_board(self, board_name: str):
        # 내비게이션 바에서 해당 게시판 이름을 가진 URL로 이동
        breadcrumb = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[@id='page-content']/div[1]/nav/ol/li[5]/a"))
        )
        board_link = breadcrumb.get_attribute("href")

        # 게시판 URL로 이동
        self.driver.get(board_link)
