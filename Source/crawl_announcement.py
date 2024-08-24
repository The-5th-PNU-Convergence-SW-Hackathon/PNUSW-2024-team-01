import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin
import re

"""
사이트 html 양식에 따라 경우를 나눔
경우 1 : 나머지 모든 공지사항 url
경우 2 : 기계공학부 공지사항
경우 3 : 대학공지
"""

class Announcement:
    def __init__(self, title: str, content_html: str, content_text: str, notice_board_name: str, url: str, files: list):
        self.title = title
        self.url = url
        self.content_html = content_html
        self.content_text = content_text
        self.notice_board_name = notice_board_name
        self.files = files

class AnnouncementPage:
    def __init__(self, page_url: str, default_url: str):
        self.page_url = page_url
        self.default_url = default_url


def clean_title(title):
    return ' '.join(title.split())  # 공지사항 제목을 한 줄로 정리

def sanitize_filename(filename):  # 파일 다운로드 시 사용할 수 없는 이름 수정
    return re.sub(r'[\/:*?"<>|]', '_', filename)


def get_anns_url(announcementPage):  # 각 사이트마다 공지 url 추출
    try:
        response = requests.get(announcementPage.page_url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(e)
        return [], announcementPage.number  # 오류 발생 시 빈 리스트 반환

    soup = BeautifulSoup(response.text, 'html.parser')
    table_element = soup.find("tbody")

    # 모든 tr 태그를 추출
    rows = table_element.find_all("tr")
    announcement_numbers = []
    urls = []

    for row in rows:
        try:
            # 첫 번째 시도: _artclTdNum 클래스의 td 태그 찾기
            number_tag = row.find("td", class_="_artclTdNum")
            number_text = number_tag.get_text(strip=True)
        except AttributeError:
            try:
                # 두 번째 시도: number 클래스의 td 태그 찾기
                number_tag = row.find("td", class_="number")
                number_text = number_tag.get_text(strip=True).replace("<br>", "").strip()
            except AttributeError:
                try:
                    # 세 번째 시도: num 클래스의 td 태그 찾기
                    number_tag = row.find("td", class_="num")
                    number_text = number_tag.get_text(strip=True).replace("<br>", "").strip()
                except AttributeError:
                    # 세 개의 시도가 모두 실패한 경우: 계속 다음으로 넘어감
                    continue

        if number_text.isdigit():  # 숫자인 경우만 처리
            announcement_numbers.append(int(number_text))

    if announcement_numbers:
        max_announcement_number = max(announcement_numbers)
        difference = max_announcement_number - announcementPage.number
        print(f'추출된 마지막 공지 번호: {max_announcement_number}')

        if difference > 0:
            print(f'{difference}개의 공지사항이 추가된 것으로 보입니다 : {announcementPage.page_url}')
        else:
            print(f'새로 추가된 공지사항 없음 : {announcementPage.page_url}.')

        # URL 추출
        for row in rows:
            # 첫 번째 시도: _artclTdNum 및 _artclTdTitle 클래스 사용
            number_tag = row.find("td", class_="_artclTdNum")
            if number_tag is None or not number_tag.get_text(strip=True).isdigit():
                try:
                    # 두 번째 시도: number 클래스 및 JavaScript URL 처리
                    number_tag = row.find("td", class_="number")
                    if number_tag is None or not number_tag.get_text(strip=True).replace("<br>", "").strip().isdigit():
                        try:
                            # 세 번째 시도: num 및 subject 클래스 사용
                            number_tag = row.find("td", class_="num")
                            if number_tag and number_tag.get_text(strip=True).isdigit():
                                announcement_number = int(number_tag.get_text(strip=True))
                                if announcement_number > announcementPage.number:
                                    title_tag = row.find("td", class_="subject")
                                    if title_tag:
                                        element = title_tag.find('a')
                                        if element:
                                            url = element['href']
                                            urls.append(urljoin(announcementPage.page_url, url))
                        except AttributeError:
                            # 세 가지 시도가 모두 실패한 경우: 계속 다음으로 넘어감
                            continue
                    else:
                        announcement_number = int(number_tag.get_text(strip=True).replace("<br>", "").strip())
                        if announcement_number > announcementPage.number:
                            element = row.find('a', href=True)
                            if element:
                                href_value = element['href']
                                if href_value.startswith("javascript:goDetail("):
                                    # 자바스크립트 매개변수 추출
                                    detail_id = href_value.split('(')[1].split(')')[0]

                                    # 실제 URL 생성 - 첫 번째 경우
                                    if "sub01_01.asp" in announcementPage.page_url:
                                        url = f"{announcementPage.page_url.split('?')[0]}?seq={detail_id}&db=hakbunotice&page=1&perPage=20&SearchPart=BD_SUBJECT&SearchStr=&page_mode=view"

                                    # 실제 URL 생성 - 두 번째 경우
                                    elif "sub01_02.asp" in announcementPage.page_url:
                                        url = f"{announcementPage.page_url.split('?')[0]}?seq={detail_id}&db=gradnotice&page=1&perPage=20&SearchPart=BD_SUBJECT&SearchStr=&page_mode=view"

                                    # 실제 URL 생성 - 세 번째 경우
                                    elif "sub01_05.asp" in announcementPage.page_url:
                                        url = f"{announcementPage.page_url.split('?')[0]}?seq={detail_id}&db=supervision&page=1&perPage=20&SearchPart=BD_SUBJECT&SearchStr=&page_mode=view"

                                    urls.append(url)
                except AttributeError:
                    # 두 번째 시도에서 실패한 경우: 계속 다음으로 넘어감
                    continue
            else:
                announcement_number = int(number_tag.get_text(strip=True))
                if announcement_number > announcementPage.number:
                    title_tag = row.find("td", class_="_artclTdTitle")
                    if title_tag:
                        element = title_tag.find('a', class_='artclLinkView')
                        if element:
                            url = element['href']
                            urls.append(urljoin(announcementPage.page_url, url))
        return urls[::-1], max_announcement_number
    else:
        print(f'공지사항을 찾을 수 없습니다 : {announcementPage.page_url}.')
        return [], announcementPage.number


def crawl_ann_partial(url: str) -> Announcement:  # 제목+내용만 부분 추출해서 중복/카테고리 판단
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(e)
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    # 첫 번째 경우: 기존 방식
    title_element = soup.find("h2", class_="artclViewTitle")
    if title_element:
        title = clean_title(title_element.get_text(strip=True))
        content_text_element = soup.find('div', class_="artclView")
        content_text = content_text_element.get_text(strip=True)
    else:
        # 두 번째 경우: vtitle 클래스의 h4 태그를 제목으로 사용, boardContents ID의 div 태그에서 내용 추출
        title_element = soup.find("h4", class_="vtitle")
        if title_element:
            title = clean_title(title_element.get_text(strip=True))
            content_text_element = soup.find('div', id="boardContents")
            content_text = content_text_element.get_text(strip=True) if content_text_element else "내용 없음"
        else:
            # 세 번째 경우: board-view 클래스의 dl 태그를 사용, board-contents clear 클래스를 사용하여 내용 추출
            title_element = soup.find("div", class_="board-view").find("dd")
            title = clean_title(title_element.get_text(strip=True)) if title_element else "제목 없음"

            content_text_element = soup.find('div', class_="board-contents clear")
            content_text = content_text_element.get_text(strip=True) if content_text_element else "내용 없음"

    return Announcement(
        title=title,
        url=url,
        notice_board_name="",
        content_html=str(content_text_element) if content_text_element else "",
        content_text=content_text,
        files=[]
    )

def crawl_ann(url: str) -> Announcement:  # 전부 추출
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(e)
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    base_url = response.url.split('/bbs/')[0]  # 기본 URL 추출

    # 첫 번째 경우: 기존 방식
    title_element = soup.find("h2", class_="artclViewTitle")
    if title_element:
        title = clean_title(title_element.get_text(strip=True))

        # 텍스트 콘텐츠 추출
        content_text_element = soup.find('div', class_="artclView")

        # HTML 콘텐츠 추출 및 이미지 URL 수정
        for img_tag in content_text_element.find_all("img"):
            img_url = img_tag.get("src")
            full_img_url = urljoin(base_url, img_url)  # 상대 URL을 절대 URL로 변환
            img_tag["src"] = full_img_url

        content_html = str(content_text_element)
    else:
        # 두 번째 경우: vtitle 클래스의 h4 태그를 제목으로 사용, boardContents ID의 div 태그에서 내용 추출
        title_element = soup.find("h4", class_="vtitle")
        if title_element:
            title = clean_title(title_element.get_text(strip=True))
            content_text_element = soup.find('div', id="boardContents")
            if content_text_element:
                # HTML 콘텐츠 추출 및 이미지 URL 수정
                for img_tag in content_text_element.find_all("img"):
                    img_url = img_tag.get("src")
                    full_img_url = urljoin(base_url, img_url)  # 상대 URL을 절대 URL로 변환
                    img_tag["src"] = full_img_url

                content_html = str(content_text_element)
            else:
                content_html = ""
                content_text_element = None
        else:
            # 세 번째 경우: board-view 클래스의 dl 태그를 사용, board-contents clear 클래스를 사용하여 내용 추출
            title_element = soup.find("div", class_="board-view").find("dd")
            title = clean_title(title_element.get_text(strip=True)) if title_element else "제목 없음"

            content_text_element = soup.find('div', class_="board-contents clear")
            if content_text_element:
                # HTML 콘텐츠 추출 및 이미지 URL 수정 (특수 처리)
                for img_tag in content_text_element.find_all("img"):
                    img_url = img_tag.get("src")
                    if img_url.startswith(".."):  # 상대 경로인 경우
                        full_img_url = urljoin("https://me.pusan.ac.kr/", img_url.replace("..\\", "").replace("../", ""))
                    elif not img_url.startswith("http"):
                        # 절대 경로이지만 도메인이 포함되지 않은 경우
                        full_img_url = urljoin("https://me.pusan.ac.kr/", img_url)
                    else:
                        full_img_url = img_url
                    img_tag["src"] = full_img_url

                content_html = str(content_text_element)
            else:
                content_html = ""
                content_text_element = None

    # 파일 다운로드 처리 (이미지 파일 제외)
    files = []
    file_extensions_to_exclude = ['.png', '.jpg', '.jpeg', '.gif']  # 제외할 파일 확장자 목록
    inserts = soup.find_all('dd', class_="artclInsert")
    os.makedirs('downloads', exist_ok=True)
    for insert in inserts:
        li_tags = insert.find_all("li")
        for li in li_tags:
            link_tag = li.find("a")
            if link_tag and 'download.do' in link_tag["href"]:
                file_url = link_tag["href"]
                full_file_url = urljoin(base_url, file_url)  # 상대 URL을 절대 URL로 변환
                file_name = sanitize_filename(link_tag.get_text(strip=True))  # 파일 이름 정리
                if not any(file_name.lower().endswith(ext) for ext in file_extensions_to_exclude):  # 이미지 파일 제외
                    file_path = os.path.join('downloads', file_name)
                    file_data = requests.get(full_file_url).content
                    with open(file_path, 'wb') as f:
                        f.write(file_data)
                    files.append(file_path)
                    print(f'파일 다운로드 완료: {file_path}')  # 파일 다운로드 완료 메시지 출력

    # 두 번째 방법: board-view-filelist 클래스 처리
    if not files:  # 기존 방법으로 파일을 찾지 못한 경우
        file_list = soup.find('ul', class_='board-view-filelist')
        if file_list:
            download_links = file_list.find_all('a', href=True)
            for link in download_links:
                file_url = urljoin(base_url, link['href'])  # 상대 URL을 절대 URL로 변환
                file_name = sanitize_filename(link.get_text(strip=True).split("\u00a0")[0].strip())  # &nbsp; 제거하고 파일명만 추출
                if not any(file_name.lower().endswith(ext) for ext in file_extensions_to_exclude):  # 이미지 파일 제외
                    file_path = os.path.join('downloads', file_name)
                    file_data = requests.get(file_url).content
                    with open(file_path, 'wb') as f:
                        f.write(file_data)
                    files.append(file_path)
                    print(f'파일 다운로드 완료: {file_path}')  # 파일 다운로드 완료 메시지 출력

    # 세 번째 방법: board-view 클래스의 dl 태그를 사용하여 파일 다운로드
    if not files:  # 기존 방법으로 파일을 찾지 못한 경우
        board_view = soup.find('div', class_='board-view')
        if board_view:
            file_tags = board_view.find_all('a', class_='add-file')
            for file_tag in file_tags:
                file_url = urljoin(base_url, file_tag['href'])  # 상대 URL을 절대 URL로 변환
                file_name = sanitize_filename(file_tag.get_text(strip=True).split('(')[0].strip())  # 파일명만 추출
                if not any(file_name.lower().endswith(ext) for ext in file_extensions_to_exclude):  # 이미지 파일 제외
                    file_path = os.path.join('downloads', file_name)
                    file_data = requests.get(file_url).content
                    with open(file_path, 'wb') as f:
                        f.write(file_data)
                    files.append(file_path)
                    print(f'파일 다운로드 완료: {file_path}')  # 파일 다운로드 완료 메시지 출력

    return Announcement(
        title=title,
        url=url,
        notice_board_name="",
        content_html=content_html,
        content_text=content_text_element.get_text(strip=True) if content_text_element else "내용 없음",
        files=files
    )
