from enum import Enum
from typing import List
from string_function import check_keywords_in_string
import requests
from bs4 import BeautifulSoup
import os


class Announcement:
    def __init__(self, title: str, content: str, notice_board_name: str, url: str, image_path: os.path):
        self.title = title
        self.url = url
        self.content = content
        self.image_path = image_path
        self.notice_board_name = notice_board_name

    def get_title(self):
        return self.title

    def get_url(self):
        return self.url

    def get_content(self):
        return self.content

    def get_image_path(self):
        return self.image_path


class AnnouncementPage:
    def __init__(self, page_url, default_url, notice_board_name) -> None:
        self.page_url = page_url
        self.default_url = default_url
        self.notice_board_name = notice_board_name


class AnnouncementPages(Enum):
    cse = AnnouncementPage(
        page_url="https://cse.pusan.ac.kr/cse/14651/subview.do?enc=Zm5jdDF8QEB8JTJGYmJzJTJGY3NlJTJGMjYwNSUyRmFydGNsTGlzdC5kbyUzRmJic09wZW5XcmRTZXElM0QlMjZpc1ZpZXdNaW5lJTNEZmFsc2UlMjZzcmNoQ29sdW1uJTNEJTI2cGFnZSUzRDElMjZzcmNoV3JkJTNEJTI2cmdzQmduZGVTdHIlM0QlMjZiYnNDbFNlcSUzRCUyNnJnc0VuZGRlU3RyJTNEJTI2",
        default_url="https://cse.pusan.ac.kr",
        notice_board_name="공모전/ 공대"
    )
    naoe = AnnouncementPage(
        page_url="http://www.naoe.pusan.ac.kr/naoe/15332/subview.do",
        default_url="http://www.naoe.pusan.ac.kr",
        notice_board_name="공모전/ 공대"
    )


def get_anns_url(announcementPage: AnnouncementPage) -> List[Announcement]:
    try:
        response = requests.get(announcementPage.page_url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(e.strerror)

    soup = BeautifulSoup(response.text, 'html.parser')
    table_element = soup.find("tbody")
    span_tags = table_element.find_all("td", "_artclTdTitle")

    table = [tag for tag in span_tags]
    urls = []

    for line in table:
        if check_keywords_in_string(line.getText(), ["대회", "공모전"]):
            element = line.find('a', class_='artclLinkView')
            if element:
                url = element['href']
            urls.append(announcementPage.default_url + url)

    return urls


def crawl_ann(url: str, annoucementPage: AnnouncementPage) -> Announcement:
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(e.strerror)

    soup = BeautifulSoup(response.text, 'html.parser')

    title_element = soup.find("h2", class_="artclViewTitle")
    title = title_element.get_text(strip=True) if title_element else "Title not found"
    main_section = soup.find('div', "artclView")
    span_tags = main_section.find_all("span")
    article = [tag.get_text().replace("\xa0", " ") + "\n" for tag in span_tags]
    print(article)
    img_tags = soup.find_all('img')
    img_path = None
    os.makedirs('images', exist_ok=True)
    for img_tag in img_tags:
        img_url = img_tag['src']
        img_name = img_url.split('/')[-1]
        img_path = os.path.join('images', img_name)

        img_data = requests.get(img_url).content
        with open(img_path, 'wb') as f:
            f.write(img_data)
            print(f'Saved {img_name}')

    inserts = soup.find('dd', "artclInsert")
    os.makedirs('downloads', exist_ok=True)
    file_path = None
    for link_tag in inserts:
        doc_url = link_tag.find("a")
        if (doc_url != -1):
            href = annoucementPage.default_url + doc_url["href"]
            file_url = href
            file_name = doc_url.get_text(strip=True)
            file_path = os.path.join('downloads', file_name)
            file_data = requests.get(file_url).content
            with open(file_path, 'wb') as f:
                f.write(file_data)
                print(f'Saved {file_name}')

    path = img_path
    if (img_path == None):
        path = file_path

    return Announcement(
        title=title,
        url=url,
        notice_board_name=annoucementPage.notice_board_name,
        content=article,
        image_path=path
    )


def crawl_anns(announcementPage: AnnouncementPage):
    urls = get_anns_url(announcementPage)
    results = []
    for url in urls:
        results.append(crawl_ann(url, announcementPage))
    return results