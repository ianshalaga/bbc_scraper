''' BBC Mundo Scraper '''

import LÑdb as db
import requests
from bs4 import BeautifulSoup
from termcolor import colored
import re
import math


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


''' Titles & Authors '''

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


''' Data original '''

def get_data_original():
    links_list = db.get_no_data_original_links()

    print(colored("Data original scraper", "magenta"))

    for news_link in links_list:
        print(colored(news_link, "yellow"))

        page = requests.get(news_link)
        soup = BeautifulSoup(page.content, "html.parser")
        results = soup.find(role="main")
        elements = results.find_all("div", dir="ltr")

        content = list()

        for element in elements:
            # Subtitles
            subtitle = element.find("h2")
            text = element.find("p", dir="ltr")
            if subtitle is not None:
                content.append("[Subtítulo] " + subtitle.text.strip())

            # Images and captions
            figure = element.find("figure")
            if figure is not None:
                link = figure.find("img")
                caption = figure.find("figcaption")
                if caption is not None:
                    paragraph = caption.find("p")
                    if paragraph is not None:
                        content.append("[Imagen] " + link["src"])
                        content.append("[Epígrafe] " + paragraph.text.strip())
                else:
                    if link.get("alt") is not None and \
                    link["alt"].lower() != "." and \
                    link["alt"].lower() != "línea" and \
                    link["alt"].lower() != "linea" and \
                    link["alt"].lower() != "line" and \
                    link["alt"].lower() != "grey line" and \
                    link["alt"].lower() != "grey_new" and \
                    link["alt"].lower() != "BBC" and \
                    link["alt"].lower() != "007 in numbers" and \
                    link["alt"].lower() != "line break":
                        content.append("[Imagen] " + link["src"])

            # Text bodies
            if text is not None:
                link = element.find("a")
                if link is not None:# and "bbc.com/mundo/noticias" not in link["href"]:
                    if link.get("href"):
                        if "bbc.com/mundo/noticias" not in link["href"]:
                            if bool(re.search(r"[aA][qQ][uU][íÍ]", text.text)) and bool(re.search(r"[pP]uedes ver", text.text)):
                                text_after = re.sub(r"[aA][qQ][uU][íÍ]", "en la descripción", text.text)
                                content.append("[Cuerpo] " + text_after)
                                content.append("[Enlace] " + link["href"])
                            else:
                                content.append("[Cuerpo] " + text.text.strip())
                                content.append("[Enlace] " + link["href"])
                else:
                    if bool(re.search(r"[aA][qQ][uU][íÍ]", text.text)) and bool(re.search(r"[pP]uedes ver", text.text)):
                        text_after = re.sub(r"[aA][qQ][uU][íÍ]", "en la descripción", text.text)
                        content.append("[Cuerpo] " + text_after)
                    else:
                        content.append("[Cuerpo] " + text.text.strip())            

            text_list = element.find("ul", dir="ltr")
            
            if text_list is not None:
                text_list = text_list.find_all("li")
                if text_list is not None:
                    for e in text_list:
                        e_link = e.find("a")
                        if e_link is None:
                            content.append("[Cuerpo] " + e.text.strip())

            # Enlaces
            link = element.find("div")
            if link is not None and link.get("data-e2e"):
                if "http" in link["data-e2e"]:
                    link_name = link["data-e2e"].split("-")[-1]
                    if "youtube" in link_name:
                        link_name = link_name.split("&")[0]
                    content.append("[Enlace] " + link_name)
            
            if link is not None:
                link = link.find("div")
                if link is not None and link.get("data-e2e"):
                    link = link.find("iframe")
                    if link is not None and link.get("src"):
                        content.append("[Enlace] " + link["src"])

        content = article_end_corrector(content)
        content = article_format_corrector(content)

        # Tags
        tags_list = list()
        tags = soup.find("aside")
        if tags is not None:
            tags1 = tags.find_all("li")
            tags2 = tags.find_all("div", class_="bbc-54c14d e1hq59l0")
            tags = tags1 + tags2
            for t in tags:
                tags_list.append(t.text.strip())
            content.append("[Etiquetas] " + ", ".join(tags_list))
        else:
            content.append("[Etiquetas] Sin etiquetas")
        
        content.append(f"[Fuente] {news_link}")

        # with open(output_route, "w", encoding="utf8") as f:
        #     f.write("\n\n".join(content))

        data_original = "\n\n".join(content)
        db.update_data_orginal(news_link, data_original)
        print(colored(news_link, "green", attrs=["bold"]))


def article_end_corrector(content_list):
    new_content_list = list()
    flag = True
    for i in range(len(content_list)):
        content_tag = content_list[i].split(" ")[0]
        content_body = " ".join(content_list[i].split(" ")[1:])
        if content_tag == "[Cuerpo]" and ("cobertura especial" in content_body or \
                                          "nuestro mejor contenido" in content_body):
            new_content_list = content_list[:i]
            flag = False
            break
    
    if flag:
        new_content_list = content_list

    if new_content_list != []:
        if new_content_list[-1].split(" ")[0] == "[Imagen]":
            new_content_list.pop(-1)

    return new_content_list


def article_format_corrector(content_list):
    data_list = list()
    for i in range(len(content_list)):
        if content_list[i].split(" ")[0] == "[Título]":
            data_list.append(content_list[i])
        if content_list[i].split(" ")[0] == "[Autor]":
            data_list.append(content_list[i])
        if content_list[i].split(" ")[0] == "[Fecha]":
            data_list.append(content_list[i])

    for e in data_list:
        content_list.remove(e)

    return data_list + content_list


''' Data arranged '''


def arranger(data_original):
    data_list = data_original.split("\n\n")

    count_subtitles = 0
    count_bodies = 0
    count_images = 0
    count_captions = 0

    for element in data_list:
        tag = element.split(" ")[0]
        if tag == "[Subtítulo]":
            count_subtitles += 1
        if tag == "[Cuerpo]":
            count_bodies += 1
        if tag == "[Imagen]":
            count_images += 1
        if tag == "[Epígrafe]":
            count_captions += 1

    bodies_by_image = 0

    if count_images > count_bodies:
        diff = count_images - count_bodies
        for e in reversed(data_list):
            if diff != 0:
                if data_list[data_list.index(e)].split(" ")[0] == "[Epígrafe]":
                    data_list[data_list.index(e)] = "[Cuerpo] " + " ".join(data_list[data_list.index(e)].split(" ")[1:])
                    diff -= 1
            else:
                break
        
        count_subtitles = 0
        count_bodies = 0
        count_images = 0
        count_captions = 0

        for element in data_list:
            tag = element.split(" ")[0]
            if tag == "[Subtítulo]":
                count_subtitles += 1
            if tag == "[Cuerpo]":
                count_bodies += 1
            if tag == "[Imagen]":
                count_images += 1
            if tag == "[Epígrafe]":
                count_captions += 1

        bodies_by_image = math.ceil(count_images / count_bodies)
    else:
        bodies_by_image = math.ceil(count_bodies / count_images)

    images_list = list()
    bodies_list = list()

    for e in data_list:
        if e.split(" ")[0] == "[Imagen]":
            if data_list[data_list.index(e)+1].split(" ")[0] == "[Epígrafe]":
                images_list.append(
                    {
                        "image": e,
                        "caption": data_list[data_list.index(e)+1]
                    }
                )
            else:
                images_list.append(
                    {
                        "image": e,
                        "caption": ""
                    }
                )
        elif e.split(" ")[0] != "[Epígrafe]":
            bodies_list.append(e)

    arranged_list = list()

    for e in images_list:
        if e["caption"] != "":
            arranged_list.append(e["image"])
            arranged_list.append(e["caption"])
        else:
            arranged_list.append(e["image"])

        start = images_list.index(e) * bodies_by_image
        end = start + bodies_by_image
        for i in range(start, end):
            arranged_list.append(bodies_list[i])

    arranged_list = arranged_list + bodies_list[len(images_list) * bodies_by_image:]

    for e in arranged_list:
        print(colored(e, "red"))




def data_arranger():
    # links_list = db.get_no_data_arranged_links()
    # print(colored("Data arranger", "magenta"))

    # for news_link in links_list:
    #     print(colored(news_link, "yellow"))
    #     data_original = db.get_data_original(news_link)
    #     arranger(data_original)

    data_original = db.get_data_original(r"https://www.bbc.com/mundo/noticias-38021766")
    arranger(data_original)


data_arranger()