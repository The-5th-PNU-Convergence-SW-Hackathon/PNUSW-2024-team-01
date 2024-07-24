import requests
from bs4 import BeautifulSoup

class Announcement:
    def __init__(self, title: str, content: str, notice_board_name: str, url: str):
        self.title = title
        self.url = url
        self.content = content
        self.notice_board_name = notice_board_name

def get_recent_anns_from_rss(rss_url: str):
    response = requests.get(rss_url)
    soup = BeautifulSoup(response.content, 'xml')
    items = soup.find_all('item')[:10]
    urls = [item.find('link').get_text() for item in items]
    return urls[::-1]  # 최신순에서 가장 오래된 순으로 변경

def crawl_ann(url: str) -> Announcement:
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(e)
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    title_element = soup.find("h2", class_="artclViewTitle")
    title = title_element.get_text(strip=True) if title_element else "Title not found"
    main_section = soup.find('div', class_="artclView")
    content = str(main_section)

    return Announcement(
        title=title,
        url=url,
        notice_board_name="",
        content=content
    )
