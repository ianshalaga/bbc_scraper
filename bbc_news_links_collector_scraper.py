import requests
from bs4 import BeautifulSoup


def load_links(file_path):
    links_list = list()
    with open(file_path, "r") as f:
        links_list = f.read().split("\n")

    links_set = set(links_list)

    return links_set


def links_extraction(url, URL_base, exclude):
    links_set = set()

    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")

    results = soup.find("body")
    links = results.find_all("a")

    for element in links:
        if element.get("href") is not None:
            if element is not None and \
            "noticias" in element["href"] and \
            element["href"].startswith("/mundo/noticias-") and \
            element["href"] not in exclude:
                link = URL_base + element["href"]
                links_set.add(link)

    return links_set


recursive_deep = 0
def scraper(url, all_links, URL_base, exclude, recursive_deep):
    if recursive_deep > 950:
        return
    else:
        recursive_deep += 1
    print(f"Recursive level: {recursive_deep}")
    links_set = links_extraction(url, URL_base, exclude)
    if links_set.issubset(all_links):
        return
    for link in links_set:
        if link not in all_links:
            all_links.add(link)
            print(link)
            scraper(link, all_links, URL_base, exclude, recursive_deep)
            

def sort_links(links_set):
    '''
    Sort news from newer to oldest.
    '''
    links_sorted = list()

    links_list = list(links_set)
    links_splitted = list()

    for e in links_list:
        split = e.split("-")
        split[-1] = int(split[-1])
        links_splitted.append(split)

    links_splitted = sorted(links_splitted, key=lambda x:x[-1], reverse=True)

    for e in links_splitted:
        links_sorted.append("-".join(e[:-1] + [str(e[-1])]))

    return links_sorted



URL_seed = "https://www.bbc.com/mundo"

URL_base = "https://www.bbc.com"

exclude = ["/mundo/noticias-58984987", # Categoría: Medio ambiente
           "/mundo/noticias-36795069", # Categoría: Hay festival
           "/mundo/noticias-43826245", # Categoría: Centroamérica cuenta
           "/mundo/noticias-48908206"] # Categoría: BBC Extra

links_set = load_links("news_links.txt")

''' Daily '''
# scraper(URL_seed, links_set, URL_base, exclude, recursive_deep)

# links_list = sort_links(links_set)

# with open("news_links.txt", "w") as f:
#     for i in range(len(links_list)):
#         if i == len(links_list)-1:
#             f.write(links_list[i])
#         else:
#             f.write(links_list[i] + "\n")


''' Brute force '''
c = 0
for e in links_set:
    c += 1
    print(f"Seed ({c}/{len(links_set)})")
    links_set2 = load_links("news_links.txt")
    scraper(e, links_set2, URL_base, exclude, recursive_deep)

    links_list = sort_links(links_set2)

    with open("news_links.txt", "w") as f:
        for i in range(len(links_list)):
            if i == len(links_list)-1:
                f.write(links_list[i])
            else:
                f.write(links_list[i] + "\n")
