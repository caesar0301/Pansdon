# encoding: utf-8
import re


def _extract_page_num(link):
    if not link:
        return -1
    match = re.search(r"(?<=\?page=)\d+", link)
    return int(match.group(0)) if match else -1


def extract_max_page(soup):
    page_counter = soup.find("div", class_ = "ui-pagechange")
    if page_counter:
        links = page_counter.find_all("a", href=True)
        pages = [-1]
        for link in links:
            pages.append(_extract_page_num(link['href']))
        return max(pages)
    return -1
