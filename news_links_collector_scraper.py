import requests
from bs4 import BeautifulSoup


def links_extraction(url, URL_base, exclude):
    links_set = set()

    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")

    results = soup.find("body")
    links = results.find_all("a")

    for element in links:
        if element is not None and \
        "noticias" in element["href"] and \
        element["href"].startswith("/mundo/noticias-") and \
        element["href"] not in exclude and \
        element.get("href") is not None:
            link = URL_base + element["href"]
            links_set.add(link)

    return links_set


def scraper(url, all_links, URL_base, exclude):
    links_set = links_extraction(url, URL_base, exclude)
    for link in links_set:
        if link not in all_links:
            all_links.add(link)
            print(link)
            scraper(link, all_links, URL_base, exclude)
            

URL_seed = "https://www.bbc.com/mundo/noticias-america-latina-59202176"

links_set = set()
links_set.add(URL_seed)

URL_base = "https://www.bbc.com"

exclude = ["/mundo/noticias-58984987", # Categoría: Medio ambiente
           "/mundo/noticias-36795069", # Categoría: Hay festival
           "/mundo/noticias-43826245", # Categoría: Centroamérica cuenta
           "/mundo/noticias-48908206"] # Categoría: BBC Extra

scraper(URL_seed, links_set, URL_base, exclude)

with open("news_links.txt", "w") as f:
    for e in links_set:
        f.write(e + "\n")