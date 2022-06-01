import requests
from bs4 import BeautifulSoup
from termcolor import colored
import csv
from pathlib import Path



# def seniority_validation(url):
#     old = False
#     split = url.split("_")
#     if len(split) > 1:
#         old = True
#     return old


def load_links(file_path):
    '''
    Loads news links from a txt file.
    '''
    links_list = list()
    with open(file_path, "r", encoding="utf-8") as f:
        links_list = f.read().split("\n")
    links_set = set(links_list)
    return links_set


def links_extraction(url, URL_base, exclude):
    '''
    Extract all news links from a given url.
    Output: Links set.
    '''
    links_set = set()

    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")

    results = soup.find("body")
    links = results.find_all("a")

    for element in links:
        if element.get("href") is not None:
            if element is not None and \
            "noticias" in element["href"] and \
            element["href"].startswith("/mundo/noticias") and \
            element["href"] not in exclude:
                link = URL_base + element["href"]
                links_set.add(link)

    return links_set


def scraper(url, all_links_set, back_up_path, URL_base, exclude, RECURSIVE_DEEP):
    '''
    Scrap news links
    Inputs:
        url: where links are gonna be scraped
        all_links_set: all links from a file in a set
        URL_base: url from news webpage
        excluded links
        recursive_deep: to control recursive limit
    '''
    if RECURSIVE_DEEP > 950:
        print(colored(f"Recursive limit reached: {RECURSIVE_DEEP}", "green"))
        return
    else:
        RECURSIVE_DEEP += 1
        print(colored(f"Recursive level: {RECURSIVE_DEEP}", "red"))
    back_up_set = load_links(back_up_path)
    if "" in back_up_set:
        back_up_set.remove("")
    all_links_set.update(back_up_set)
    links_set = links_extraction(url, URL_base, exclude)
    if links_set.issubset(all_links_set):
        return
    for link in links_set:
        if link not in all_links_set:
            all_links_set.add(link)
            with open(back_up_path, "a", encoding="utf-8") as f:
                f.write(link + "\n")
            print(colored(link, "yellow"))
            scraper(link, all_links_set, back_up_path, URL_base, exclude, RECURSIVE_DEEP)


def scraper_daily(url, all_links_path, back_up_path, URL_base, exclude, RECURSIVE_DEEP):
    print(colored("Running daily scraper", "green"))
    all_links_set = load_links(all_links_path)
    scraper(url, all_links_set, back_up_path, URL_base, exclude, RECURSIVE_DEEP)
    all_links_list = list(all_links_set)
    with open(all_links_path, "w", encoding="utf-8") as f:
        f.write("\n".join(all_links_list))


def scraper_brute_force(all_links_path, back_up_path, URL_base, exclude, RECURSIVE_DEEP):
    print(colored("Running brute force scraper", "green"))
    all_links_set = load_links(all_links_path)
    c = 0
    for e in all_links_set:
        c += 1
        print(colored(f"Current seed ({c}/{len(all_links_set)}): {e}", "green"))
        all_links_set2 = load_links(all_links_path)
        scraper(e, all_links_set2, back_up_path, URL_base, exclude, RECURSIVE_DEEP)
        all_links_list = list(all_links_set2)
        with open(all_links_path, "w", encoding="utf-8") as f:
            for i in range(len(all_links_list)):
                if i == len(all_links_list)-1:
                    f.write(all_links_list[i])
                else:
                    f.write(all_links_list[i] + "\n")


def sort_links_by_date(all_links_path, sorted_links_path):
    links_list = list()
    with open(all_links_path, "r", encoding="utf-8") as f: # Open links to sort from file into list
        links_list = f.read().split("\n")

    sorted_links_path = Path(sorted_links_path)
    sorted_links_path.touch(exist_ok=True) # Create sorted links file if it doesn't exist
    date_links_set = set()
    with open(sorted_links_path, "r", encoding="utf-8") as f: # Open sorted links from file
        csv_reader = csv.reader(f, delimiter=',', quoting=csv.QUOTE_ALL)
        # print(list(csv_reader))
        for date_link in csv_reader:
            date_links_set.add(date_link[3]) # Add the link to the set not the date
    print(date_links_set)

    for e in links_list:
        if e in date_links_set:
            continue
        date = ""
        page = requests.get(e)
        soup = BeautifulSoup(page.content, "html.parser")
        date = soup.find("time", class_="bbc-14xtggo e4zesg50")["datetime"].split("-")
        # with open(sorted_links_path, "a", encoding="utf-8") as f:
            

        # print(date + [e])


def sort_links(links_set):
    '''
    Sort news from newer to oldest.
    '''
    links_sorted = list()

    links_list = list(links_set)
    links_splitted = list()

    for e in links_list:
        # if seniority_validation(e):
        #     continue

        split = e.split("-")
        # split_old = e.split("_")
        # if len(split_old) > 1:
        #     continue

        split[-1] = int(split[-1])
        links_splitted.append(split)

    links_splitted = sorted(links_splitted, key=lambda x:x[-1], reverse=True)

    for e in links_splitted:
        links_sorted.append("-".join(e[:-1] + [str(e[-1])]))

    return links_sorted



''' ------------------------------------------------------------------------ '''

RECURSIVE_DEEP = 0 # Always needed

URL_seed = "https://www.bbc.com/mundo"
URL_base = "https://www.bbc.com"

exclude = ["/mundo/noticias-58984987", # Categoría: Medio ambiente
           "/mundo/noticias-36795069", # Categoría: Hay festival
           "/mundo/noticias-43826245", # Categoría: Centroamérica cuenta
           "/mundo/noticias-48908206"] # Categoría: BBC Extra

all_links_path = "modules/scraping/news_links.txt"
back_up_path = "modules/scraping/back_up_links.txt"
sorted_links_path = "modules/scraping/sorted_links.csv"

scraper_daily(URL_seed, all_links_path, back_up_path, URL_base, exclude, RECURSIVE_DEEP)
scraper_brute_force(all_links_path, back_up_path, URL_base, exclude, RECURSIVE_DEEP)

# sort_links_by_date(all_links_path, sorted_links_path)