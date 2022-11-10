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
    dates_dict = dict() # KEY: news_link_url; VALUE: date object (year, month, day)
    title_dict = dict() # KEY: news_link_url; VALUE: title string
    authors_dict = dict() # KEY: news_link_url; VALUE: author string
    news_links_set = db.get_news_links() # All news links in database
    links_set = set() # Valid news links to save into database
    page = requests.get(url_seed) # HTTP request
    soup = BeautifulSoup(page.content, "html.parser") # Page content parsed
    results = soup.find("body") # Find body html tag
    links = results.find_all("a") # Find all a html tags
    for element in links:
        if element is not None:
            if element.get("href") is not None: # URL exists
                # News link validation
                if "noticias" in element["href"] and \
                "cluster_" not in element["href"] and \
                element["href"].startswith("/mundo/noticias"):
                    link = url_base + element["href"] # Full link construction
                    page_obj = requests.get(link) # Link HTML request
                    link_url = page_obj.url # Get link request url
                    status_code = page_obj.status_code # Get link request status code
                    if link_url not in news_links_set: # The link is not in the database
                        date = new_date_extractor(link_url) # Get news link date
                        title = news_title_extractor(link_url) # Get news link title
                        author = news_author_extractor(link_url) # Get news link author
                        # News link validation
                        if status_code not in db.STATUS_CODES_ERROR and \
                        date != [] and \
                        title != "":
                            date_obj = Date(date[0], date[1], date[2])
                            dates_dict[link_url] = date_obj
                            title_dict[link_url] = title
                            authors_dict[link_url] = author
                            links_set.add(link_url)
    for link in links_set:
        code = new_code_extractor(link)
        if code != "": # Only if the news link has code number
            db.insert_new_link(link,
                            NEW_SOURCE,
                            code,
                            title_dict[link],
                            authors_dict[link],
                            dates_dict[link].year,
                            dates_dict[link].month,
                            dates_dict[link].day,
            )
            print(colored(f"Added: {link}", "magenta"))
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
    scraper_links(URL_SEED, URL_BASE, RECURSIVE_DEEP, EXCLUDED_SET)
    news_links_list = db.get_news_links()
    c = 0
    for link in news_links_list:
        c += 1
        print(f"Current seed ({c}/{len(news_links_list)}):", colored(link, "green"))
        scraper_links(link, URL_BASE, RECURSIVE_DEEP, EXCLUDED_SET)


def news_codes_extractor():
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
    

def new_code_extractor(new_link):
    new_code = ""
    matches = re.findall("\d+", new_link) # String numbers
    for i in range(len(matches)): # Integer convertion
        matches[i] = int(matches[i])
    if matches != []:
        new_code = str(max(matches))        
    return new_code


def new_date_extractor(new_link):
    date = list()
    page = requests.get(new_link)
    soup = BeautifulSoup(page.content, "html.parser")
    soup = soup.find(role="main")
    if soup is not None:
        soup = soup.find("time")
        if soup is not None:
            date = soup["datetime"].split("-")
    return date


def news_title_extractor(news_link):
    title = ""
    page = requests.get(news_link)
    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find(role="main")
    elements = results.find_all("div", dir="ltr")
    for element in elements:
        header = element.find("h1", id="content")
        if header is not None:
            title = header.text.strip()
            break
        header = element.find("strong", class_="e8stly50 bbc-jpo7yf e14hemmw1")
        if header is not None:
            title = header.text.strip()
            break
    return title


def news_author_extractor(news_link):
    author = ""
    author_count = 0
    page = requests.get(news_link)
    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find(role="main")
    elements = results.find_all("div", dir="ltr")
    for element in elements:
        person = element.find_all("li", role="listitem")
        if person is not None and person != [] and author_count == 0:
            for e in person:
                link = e.find("a")
                if link is None:
                    author += e.text.strip() + ". "
            author_count += 1
    return author


def news_dates_extractor():
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
    date = new_date_extractor(link)
    if "cluster_" in link or \
    status_code in db.STATUS_CODES_ERROR or \
    date == []:
        print(colored("Deleting:", "red"), colored(link, "yellow"))
        db.delete_new(link)
    else:
        print(colored("OK!", "green", attrs=["bold"]), colored(link, "yellow"), colored(date, "red"))
    #     date_obj = Date(date[0], date[1], date[2])
    #     db.update_new_valid(link, True)
    #     db.update_new_excluded(link, False)
    #     db.update_new_date(link, date_obj)

def db_clean_repeated():
    news_links_list = db.get_news_links()
    for new in news_links_list:
        links_list = news_links_list.copy()
        links_list.remove(new)
        for link in links_list:
            if new in link:
                print(colored("Deleting:", "red"), colored(link, "yellow"))
                db.delete_new(link)
    

def db_renew_links():
    news_links_list = db.get_news_links()
    for link in news_links_list:
        url = requests.get(link).url
        if url != link:
            print(colored("Updated:", "red"))
            print(colored(link, "yellow"))
            print(colored(url, "yellow"))
            db.update_new_link(link, url)
        else:
            print(colored("OK:", "green"))
            print(colored(link, "yellow"))
            print(colored(url, "yellow"))

# news_links_extractor(URL_SEED, URL_BASE)
# scraper_links(URL_SEED, URL_BASE, RECURSIVE_DEEP, EXCLUDED_SET)
# scraper_brute_force(URL_BASE, RECURSIVE_DEEP, EXCLUDED_SET)

def content_scraper_batch():
    # Traer links desde la base de datos
    # Para cada link:
    #   Extraer el contenido y guardarlo en la base de datos
    #   Arreglar el contendio y guardarlo en la base de datos
    return


def get_titles_and_authors():
    links_list = db.get_no_title_no_author_links()

    print(colored("Titles & Authors scraper", "magenta"))

    for link in links_list:
        page = requests.get(link)
        soup = BeautifulSoup(page.content, "html.parser")
        results = soup.find(role="main")
        elements = results.find_all("div", dir="ltr")

        title = ""
        author = ""
        author_count = 0

        for element in elements:
            # Title
            header = element.find("h1", id="content")
            if header is not None:
                title = header.text.strip()

            header = element.find("strong", class_="e8stly50 bbc-jpo7yf e14hemmw1")
            if header is not None:
                title = header.text.strip()

            if title != "":
                db.update_title(link, title)

            # Author
            person = element.find_all("li", role="listitem")
            if person is not None and \
            person != [] \
            and author_count == 0:
                for e in person:
                    link2 = e.find("a")
                    if link2 is None:
                        author += e.text.strip() + ". "
                if author != "":
                    db.update_author(link, author)
                author_count += 1
            
        print(colored(link, "red"))
        print(colored(title, "green"))
        print(colored(author, "yellow"))