import requests
from bs4 import BeautifulSoup
from termcolor import colored
import csv
from pathlib import Path


def load_links(file_path):
    '''
    Loads news links from a txt file into a set.
    '''
    links_list = list()
    with open(file_path, "r", encoding="utf-8") as f:
        links_list = f.read().split("\n")
    links_set = set(links_list)
    return links_set


def links_extraction(url, URL_base, excluded_links_set):
    '''
    Scrap all news links from a given url.
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
            element["href"] not in excluded_links_set:
                link = URL_base + element["href"]
                links_set.add(link)

    return links_set


def scraper(url, all_links_set, back_up_path, excluded_links_path, URL_base, RECURSIVE_DEEP):
    '''
    Scrap news links
    Inputs:
        url: where links are gonna be scraped
        all_links_set: all links from a file in a set
        URL_base: url from news webpage
        excluded links
        recursive_deep: to control recursive limit
    '''
    if RECURSIVE_DEEP > 950: # Control recursive limit
        print(colored(f"Recursive limit reached: {RECURSIVE_DEEP}", "green"))
        return
    else:
        RECURSIVE_DEEP += 1
        print(colored(f"Recursive level: {RECURSIVE_DEEP}", "red"))

    # Load back up links
    back_up_path = Path(back_up_path)
    back_up_path.touch(exist_ok=True) # Create excluded links file if it doesn't exist
    back_up_set = load_links(back_up_path)
    if "" in back_up_set: # Remove empty string
        back_up_set.remove("")
    all_links_set.update(back_up_set)

    # Load excluded link
    excluded_links_path = Path(excluded_links_path)
    excluded_links_path.touch(exist_ok=True) # Create excluded links file if it doesn't exist
    excluded_links_set = load_links(excluded_links_path)
    
    links_set = links_extraction(url, URL_base, excluded_links_set)
    if links_set.issubset(all_links_set): # Discard subset
        return

    for link in links_set:
        if link not in all_links_set: # For new links
            all_links_set.add(link)
            with open(back_up_path, "a", encoding="utf-8") as f: # Back up scraped links
                f.write(link + "\n")
            print(colored(link, "yellow"))
            scraper(link, all_links_set, back_up_path, excluded_links_path, URL_base, RECURSIVE_DEEP)


def scraper_daily(url, all_links_path, back_up_path, excluded_links_path, URL_base, RECURSIVE_DEEP):
    '''
    Scrap links from a given URL
    url: where scrap links
    all_links_path: file to load and save links
    back_up_path: restoration file in case of interruptions
    URL_base: base URL of the given URL
    excluded_links_path: URLs to exclude in the scraping process
    RECURSIVE_DEEP: global variable that controls the recursive stack to prevent overflow
    '''
    print(colored("Running daily scraper", "green"))
    all_links_set = load_links(all_links_path)
    scraper(url, all_links_set, back_up_path, excluded_links_path, URL_base, RECURSIVE_DEEP)
    all_links_list = list(all_links_set)
    with open(all_links_path, "w", encoding="utf-8") as f:
        f.write("\n".join(all_links_list))


def scraper_brute_force(all_links_path, back_up_path, excluded_links_path, URL_base, RECURSIVE_DEEP):
    '''
    Scrap links from from all URLs in all_links_path file
    all_links_path: file to load and save links
    back_up_path: restoration file in case of interruptions
    URL_base: base URL of the given URL
    excluded_links_path: URLs to exclude in the scraping process
    RECURSIVE_DEEP: global variable that controls the recursive stack to prevent overflow
    '''
    print(colored("Running brute force scraper", "green"))
    all_links_set = load_links(all_links_path)
    c = 0
    for e in all_links_set:
        c += 1
        print(colored(f"Current seed ({c}/{len(all_links_set)}): {e}", "green"))
        all_links_set2 = load_links(all_links_path)
        scraper(e, all_links_set2, back_up_path, excluded_links_path, URL_base, RECURSIVE_DEEP)
        all_links_list = list(all_links_set2)
        with open(all_links_path, "w", encoding="utf-8") as f:
            for i in range(len(all_links_list)):
                if i == len(all_links_list)-1:
                    f.write(all_links_list[i])
                else:
                    f.write(all_links_list[i] + "\n")


def sort_links_by_date(all_links_path, scraped_dates_path, sorted_links_path, excluded_links_path):
    '''
    Sort links ascendent by publication date
    all_links_path: file to load links
    scraped_dates_path: file to save links dates
    sorted_links_path: file where sorted links are saved
    excluded_links_path: file for excluded links
    '''
    print(colored("Running dates algorithm", "green"))

    # Load links
    links_list = list()
    with open(all_links_path, "r", encoding="utf-8") as f: # Open links to sort from file into list
        links_list = f.read().split("\n")

    # Load scraped dates temporal
    scraped_dates_path = Path(scraped_dates_path)
    scraped_dates_path.touch(exist_ok=True) # Create sorted links file if it doesn't exist
    date_links_set = set()
    with open(scraped_dates_path, "r", encoding="utf-8") as f: # Open sorted links from file
        csv_reader = csv.reader(f, delimiter=',', quoting=csv.QUOTE_ALL)
        for date_link in csv_reader:
            date_links_set.add(date_link[3]) # Add the link to the set not the date
    if "" in date_links_set: # Remove empty string
        date_links_set.remove("")

    # Load excluded link
    excluded_links_set = load_links(excluded_links_path)
    if "" in excluded_links_set: # Remove empty string
        excluded_links_set.remove("")

    # Dates scraper
    for link in links_list:
        if link in date_links_set: # Don't scrap dates already scraped
            continue
        page = requests.get(link)
        soup = BeautifulSoup(page.content, "html.parser")
        soup = soup.find("time")
        if soup is not None:
            date = soup["datetime"].split("-")
            with open(scraped_dates_path, "a", encoding="utf-8", newline="") as f: # Save dates into file
                csv_writer = csv.writer(f, delimiter=",")
                csv_writer.writerow(date + [link])
            print(colored(date, "green", attrs=["bold"]), colored(link, "yellow"))
        elif link not in excluded_links_set:
            print("Excluded:", colored(link, "blue", attrs=["bold"]))
            excluded_links_set.add(link)
            with open(excluded_links_path, "w", encoding="utf-8") as f:
                f.write("\n".join(excluded_links_set))

    # Sort links by date PENDING @@@@


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
excluded_links_path = "modules/scraping/excluded_links.txt"
scraped_dates_path = "modules/scraping/scraped_dates.csv"
sorted_links_path = "modules/scraping/sorted_links.csv"

scraper_daily(URL_seed, all_links_path, back_up_path, excluded_links_path, URL_base, RECURSIVE_DEEP)
# scraper_brute_force(all_links_path, back_up_path, excluded_links_path, URL_base, RECURSIVE_DEEP)

sort_links_by_date(all_links_path, scraped_dates_path, sorted_links_path, excluded_links_path)