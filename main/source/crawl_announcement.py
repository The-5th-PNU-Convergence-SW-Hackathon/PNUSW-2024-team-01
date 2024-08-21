import requests
from bs4 import BeautifulSoup
import os
from typing import List
from urllib.parse import urljoin


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


def get_anns_url(announcementPage: AnnouncementPage) -> List[str]:
    try:
        response = requests.get(announcementPage.page_url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(e)
        return []  # 오류 발생 시 빈 리스트 반환

    soup = BeautifulSoup(response.text, 'html.parser')
    table_element = soup.find("tbody")

    # 모든 _artclTdNum 클래스의 td 태그 추출
    number_tags = table_element.find_all("td", class_="_artclTdNum")
    announcement_numbers = []

    # 각 _artclTdNum 태그에서 숫자만 추출하여 리스트에 추가
    for number_tag in number_tags:
        number_text = number_tag.get_text(strip=True)
        if number_text.isdigit():  # 숫자인 경우만 추가
            announcement_numbers.append(int(number_text))

    announcement_number = max(announcement_numbers)
    print(f'추출된 마지막 공지 번호: {announcement_number}')

    # announcementPage.number와 비교
    if announcement_number > announcementPage.number:
        # 번호 차이 계산
        difference = announcement_number - announcementPage.number
        print(f'{difference}개의 공지사항이 추가된 것으로 보입니다 : {announcementPage.page_url}')

        span_tags = table_element.find_all("td", class_="_artclTdTitle")
        urls = []

        # 최대 difference개의 URL만 추출
        for line in span_tags:
            if len(urls) >= difference:
                break
            element = line.find('a', class_='artclLinkView')
            if element:
                url = element['href']
                urls.append(urljoin(announcementPage.default_url, url))  # 상대 URL을 절대 URL로 변환

        return urls, announcement_number
    else:
        print(f'새로 추가된 공지사항 없음 : {announcementPage.page_url}.')
        return [], announcement_number



def crawl_ann_partial(url: str) -> Announcement:
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(e)
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    title_element = soup.find("h2", class_="artclViewTitle")
    title = clean_title(title_element.get_text(strip=True))

    # 텍스트 콘텐츠 추출
    content_text_element = soup.find('div', class_="artclView")
    content_text = content_text_element.get_text(strip=True)

    return Announcement(
        title=title,
        url=url,
        notice_board_name="",
        content_html="",
        content_text=content_text,
        files=[]
    )


def crawl_ann(url: str) -> Announcement:
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(e)
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    base_url = response.url.split('/bbs/')[0]  # 기본 URL 추출

    title_element = soup.find("h2", class_="artclViewTitle")
    title = clean_title(title_element.get_text(strip=True))

    # 텍스트 콘텐츠 추출
    content_text_element = soup.find('div', class_="artclView")

    # HTML 콘텐츠 추출 및 이미지 URL 수정
    for img_tag in content_text_element.find_all("img"):
        img_url = img_tag.get("src")
        full_img_url = urljoin(base_url, img_url)  # 상대 URL을 절대 URL로 변환
        img_tag["src"] = full_img_url

    content_html = str(content_text_element)

    # 파일 다운로드
    inserts = soup.find_all('dd', class_="artclInsert")
    os.makedirs('downloads', exist_ok=True)
    files = []
    for insert in inserts:
        li_tags = insert.find_all("li")
        for li in li_tags:
            link_tag = li.find("a")
            if link_tag and 'download.do' in link_tag["href"]:
                file_url = link_tag["href"]
                full_file_url = urljoin(base_url, file_url)  # 상대 URL을 절대 URL로 변환
                file_name = link_tag.get_text(strip=True)
                file_path = os.path.join('downloads', file_name)
                file_data = requests.get(full_file_url).content
                with open(file_path, 'wb') as f:
                    f.write(file_data)
                files.append(file_path)
                print(f'파일 다운로드 완료: {file_path}')  # 파일 다운로드 완료 메시지 출력

    return Announcement(
        title=title,
        url=url,
        notice_board_name="",
        content_html=content_html,
        content_text=content_text_element.get_text(strip=True),
        files=files
    )
