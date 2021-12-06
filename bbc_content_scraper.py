import requests
from bs4 import BeautifulSoup
from pathlib import Path
import os
import re
import csv



def flatten_body(content_list):
    '''
    Join continous text bodies.
    '''
    flatten_list = list()
    content_list.pop(-1)
    body = ""
    for i in range(len(content_list)-1):
        if content_list[i].split(" ")[0] == "[Cuerpo]":
            text = " ".join(content_list[i].split(" ")[1:])
            if list(text)[-1] != ".":
                body += text + ". "    
            else:
                body += text + " "
            if content_list[i+1].split(" ")[0] != "[Cuerpo]":
                flatten_list.append("[Cuerpo] " + body)
                body = ""
        else:
            flatten_list.append(content_list[i])

    return flatten_list


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

    if new_content_list[-1].split(" ")[0] == "[Imagen]":
        new_content_list.pop(-1)

    return new_content_list


def article_format_corrector(content_list):
    data_list = list()
    new_content_list = list()
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


def bbc_content_scraper(URL, output_route):
    '''
    Scrap content, with tags, from a given URL into a text file.
    '''

    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")

    results = soup.find(role="main")
    elements = results.find_all("div", dir="ltr")

    title = ""
    date = ""
    author = ""
    author_count = 0
    content = list()

    for element in elements:
        # Title
        header = element.find("h1", id="content")
        if header is not None:
            title = header.text.strip()
            content.append("[Título] " + title)

        header = element.find("strong", class_="e8stly50 bbc-jpo7yf e14hemmw1")
        if header is not None:
            title = header.text.strip()
            content.append("[Título] " + title)

        # Date
        pub_date = element.find_all("time", class_="bbc-14xtggo e4zesg50")
        if pub_date is not None and pub_date != []:
            date = pub_date[-1]["datetime"]
            content.append("[Fecha] " + date)

        # Author
        person = element.find_all("li", role="listitem")
        if person is not None and person != [] and author_count == 0:
            for e in person:
                link = e.find("a")
                if link is None:
                    author += e.text.strip() + ". "
            if author != "":
                content.append("[Autor] " + author)
            author_count += 1

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
                if link.get("alt") is not None and link["alt"].lower() != "línea":
                    content.append("[Imagen] " + link["src"])

        # Text bodies
        if text is not None:
            if bool(re.search(r"[aA][qQ][uU][íÍ]", text.text)) and bool(re.search(r"[pP]uedes ver", text.text)):
                text_after = re.sub(r"[aA][qQ][uU][íÍ]", "en la descripción", text.text)
                content.append("[Cuerpo] " + text_after)
            else:
                content.append("[Cuerpo] " + text.text.strip())
            
            link = element.find("a")
            if link is not None:
                content.append("[Enlace] " + link["href"])

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
    
    content.append(f"[Fuente] {URL}")

    with open(output_route, "w", encoding="utf8") as f:
        f.write("\n\n".join(content))


def bbc_content_scraper_batch(news_links_path):
    # Load links
    links_list = list()
    with open(news_links_path, "r", encoding="utf8") as f:
        links_list = f.read().split("\n")    

    # News scraping
    c = 0
    for link in links_list:
        c += 1
        print(f"Scraping {c}/{len(links_list)}: {link}")
        article_id = link.split("-")[-1]
        p = Path(f"bbc_news_content_scraped/{article_id}")
        if not(p.exists()):
            p.mkdir(exist_ok=True)
            output_path = os.path.join(p, article_id + ".txt")
            bbc_content_scraper(link, output_path)
        else:
            output_path = Path(os.path.join(p, article_id + ".txt"))
            if not(output_path.exists()):
                bbc_content_scraper(link, output_path)


def tags_extractor(article_path):
    tags = list()
    content_list = list()
    with open(article_path, "r", encoding="utf8") as f:
        content_list = f.read().split("\n\n")
    for element in content_list:
        tag = element.split(" ")[0]
        if tag == "[Etiquetas]":
            tags = " ".join(element.split(" ")[1:]).split(", ")
    for i in range(len(tags)):
        tags[i] = tags[i].lower()
    return tags


def id_tags_generator():
    news_scraped_path = Path("bbc_news_content_scraped")
    ids_list = list()
    c = 1
    total = len(list(news_scraped_path.iterdir()))
    for folder in news_scraped_path.iterdir():
        article_path = os.path.join(folder, folder.name + ".txt")
        tags = tags_extractor(article_path)
        csv_list = [folder.name] + tags
        ids_list.append(csv_list)
        print(f"{c}/{total} - {csv_list}")
        c += 1
    with open("news_id_tags.csv", "w", encoding="utf8", newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=",", quoting=csv.QUOTE_MINIMAL)
        writer.writerows(ids_list)



news_links_path = Path("news_links.txt")
bbc_content_scraper_batch(news_links_path)
id_tags_generator()

# TESTING
# URL = "https://www.bbc.com/mundo/noticias-59420272"
# URL = "https://www.bbc.com/mundo/noticias-51912396"
# URL = "https://www.bbc.com/mundo/noticias-internacional-51112564"
# URL = "https://www.bbc.com/mundo/noticias-59432415"
# article_id = URL.split("-")[-1]
# p = Path(f"bbc_news_content_scraped/{article_id}")
# p.mkdir(exist_ok=True)
# output_route = Path(f"bbc_news_content_scraped/{article_id}/{article_id}" + ".txt")
# bbc_content_scraper(URL, output_route)