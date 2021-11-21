import requests
from bs4 import BeautifulSoup
import json
import re
import string
import os


def get_file_name(name):
    new_name = name.replace(" ", "_")
    return f"{new_name}.txt"

def get_url(half):
    return f"https://www.nature.com{half}"


def write_file(url, file_name):
    r = requests.get(url, headers={'Accept-Language': 'en-US,en;q=0.5'})
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, "html.parser")
        body = soup.find('div', {'class': "c-article-body"})
        page_content = body.text.strip()
        file = open(file_name, 'w')
        file.write(page_content)
        file.close()


def scrap_page(r, search_type, folder):
    soup = BeautifulSoup(r.text, "html.parser")
    titles = soup.find_all('h3', class_="c-card__title")
    tags = soup.find_all('span', {"data-test":"article.type"})
    links = soup.find_all('a', {"itemprop":"url"})
    for a, b, c in zip(titles, tags, links):
        if b.text.strip() == search_type:
            file_name = get_file_name(a.text.strip())
            path = os.path.join(folder, file_name)
            new_url = get_url(c.get('href'))
            write_file(new_url, path)


def scrap_news(url, page_num, article_type):
    for n in range(1, page_num + 1):
        p = {'page': str(n)}
        response = requests.get('https://www.nature.com/nature/articles?sort=PubDate&year=2020', params=p)
        if response.status_code == 200:
            folder_name = f'Page_{n}'
            if not os.access(folder_name, os.R_OK):
                os.mkdir(folder_name)
            scrap_page(response, article_type, folder_name)


def get_json(url):
    r = requests.get(url, headers={'Accept-Language': 'en-US,en;q=0.5'})
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, "html.parser")
        j = soup.find("script", {"type": "application/ld+json"})
        if j:
            return json.loads("".join(j.contents))


def get_movie_summary(raw_text):
    d = {}
    if "@type" in raw_text:
        if raw_text["@type"] == "Movie" or raw_text["@type"] == "TVSeries":
            if "name" in raw_text and "description" in raw_text:
                title = raw_text["name"]
                title = title.replace("&apos;", "'")
                d["title"] = title
                d["description"] = raw_text["description"]
                return d


def main():
    url = "https://www.nature.com/nature/articles?sort=PubDate&year=2020&page=3"
    page_num = int(input())
    article_type = input()
    scrap_news(url, page_num, article_type)


if __name__ == "__main__":
    main()
