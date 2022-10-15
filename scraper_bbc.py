''' BBC Mundo Scraper '''

import LÑdb as db
import requests
from bs4 import BeautifulSoup
from termcolor import colored
import re


''' Globals variables '''

URL_SEED = "https://www.bbc.com/mundo"
URL_BASE = "https://www.bbc.com"
NEW_SOURCE = "BBC"
RECURSIVE_DEEP = 0 # Always needed
EXCLUDED_SET = set() # Link already scraped


class Date:
    def __init__(self, year, month, day):
        self.year = year
        self.month = month
        self.day = day


def news_links_extractor(url_seed, url_base):
    '''
    Scrap all news links from a given url.
    Inputs:
        url_seed: where to scrap news links from.
        url_base: url base of news' source.
    Output: Links set.
    '''
    # error_codes = [404, 500]
    news_links_set = db.get_news_links()
    links_set = set()
    page = requests.get(url_seed)
    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find("body")
    links = results.find_all("a")
    for element in links:
        if element.get("href") is not None:
            link = url_base + element["href"]
            if element is not None and \
            "noticias" in element["href"] and \
            "cluster_" not in element["href"] and \
            element["href"].startswith("/mundo/noticias") and \
            link not in news_links_set:
                status_code = requests.get(link).status_code
                if status_code not in db.STATUS_CODES_ERROR:
                    links_set.add(link)
    for link in links_set:
        db.insert_new_link(link, NEW_SOURCE)
    return links_set


def scraper_links(url_seed, url_base, recursive_deep, excluded_set):
    '''
    Scrap news links.
    Inputs:
        url_seed: where to scrap news links from
        url_base: url base of news' source
        recursive_deep: to control recursive limit
        excluded_set: URLs to exclude in the scraping process
    '''
    if recursive_deep > 950: # Control recursive limit
        print(colored(f"Recursive limit reached: {recursive_deep}", "green"))
        return
    else:
        recursive_deep += 1
        print(colored(f"Recursive level: {recursive_deep}", "red"))

    links_set = news_links_extractor(url_seed, url_base)
    for link in links_set:
        if link not in EXCLUDED_SET:
            EXCLUDED_SET.add(link)
            print(colored(link, "yellow"))
            scraper_links(link, url_base, recursive_deep, excluded_set)
    

def scraper_links_daily():
    '''
    For daily running.
    '''
    print(colored("Running DAILY scraper", "green"))
    scraper_links(URL_SEED, URL_BASE, RECURSIVE_DEEP, EXCLUDED_SET)


def scraper_links_brute_force():
    '''
    For deep links extraction.
    '''
    print(colored("Running BRUTE FORCE scraper", "green"))
    news_links_list = db.get_news_links()
    c = 0
    for link in news_links_list:
        c += 1
        print(f"Current seed ({c}/{len(news_links_list)}):", colored(link, "green"))
        scraper_links(link, URL_BASE, RECURSIVE_DEEP, EXCLUDED_SET)


def new_code_number_extractor():
    no_code_links_set = db.get_no_code_links()
    for link in no_code_links_set:
        code_number = ""
        matches = re.findall("\d+", link) # String numbers
        for i in range(len(matches)): # Integer convertion
            matches[i] = int(matches[i])
        if matches != []:
            code_number = str(max(matches))
            print("Link:", colored(link, "green"), "Code:", colored(code_number, "yellow"))
            db.update_new_code(link, code_number)
            db.update_new_valid(link, True)
            db.update_new_excluded(link, False)
        else:
            print("Link:", colored(link, "green"), colored("Invalid", "red"))
            db.update_new_valid(link, False)
            db.update_new_excluded(link, True)
    

def new_date_extractor():
    no_date_links_set = db.get_no_date_links()
    for link in no_date_links_set:
        page = requests.get(link)
        soup = BeautifulSoup(page.content, "html.parser")
        soup = soup.find(role="main")
        if soup is not None:
            soup = soup.find("time")
            if soup is not None:
                date = soup["datetime"].split("-")
                if date == []:
                    print("Link:", colored(link, "green"), colored("Invalid", "red"))
                    db.update_new_valid(link, False)
                    db.update_new_excluded(link, True)
                else:
                    date_obj = Date(date[0], date[1], date[2])
                    print("Link:", colored(link, "green"), "Date:", colored(date, "red"))
                    db.update_new_valid(link, True)
                    db.update_new_excluded(link, False)
                    db.update_new_date(link, date_obj)


def db_cleaner():
  news_links_list = db.get_news_links()
  for link in news_links_list:
    status_code = requests.get(link).status_code
    if "cluster_" in link or status_code in db.STATUS_CODES_ERROR:
      print(colored("Deleting:", "red"), colored(link, "yellow"))
      db.delete_new(link)

# news_links_extractor(URL_SEED, URL_BASE)
# scraper_links(URL_SEED, URL_BASE, RECURSIVE_DEEP, EXCLUDED_SET)
# scraper_brute_force(URL_BASE, RECURSIVE_DEEP, EXCLUDED_SET)
