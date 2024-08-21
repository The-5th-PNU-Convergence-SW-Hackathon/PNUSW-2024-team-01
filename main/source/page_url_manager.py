import pandas as pd

def extract_domain_part(url, domain):
    domain_index = url.find(domain)
    if domain_index == -1:
        return url

    path_start_index = url.find('/', domain_index + len(domain))
    if path_start_index == -1:
        return url
    else:
        return url[:path_start_index]

class AnnouncementPage:
    def __init__(self, page_url, default_url, number=0) -> None:
        self.page_url = page_url
        self.default_url = default_url
        self.number = number  # 공지 번호 추가, 기본값은 0

class PageUrlManager:
    def __init__(self):
        filename = "C:\\together-main\\Source\\pages.csv"
        df = pd.read_csv(filename)
        self.announcement_pages = []
        self.__init_announcement_pages(df)

    def __init_announcement_pages(self, data):
        for _, row in data.iterrows():
            page_url = row['page_url']
            # number가 없거나 NaN인 경우 0으로 처리
            number_str = str(row['number']) if 'number' in row and pd.notna(row['number']) else "0"
            # 소수점을 포함한 숫자인 경우, float로 변환 후 int로 변환
            number = int(float(number_str))
            self.announcement_pages.append(
                AnnouncementPage(
                    page_url=page_url,
                    default_url=extract_domain_part(page_url, "pusan.ac.kr"),
                    number=number
                )
            )

