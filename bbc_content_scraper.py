import requests
from bs4 import BeautifulSoup
from pathlib import Path
import os



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
    if content_list[-1].split(" ")[0] == "[Cuerpo]" and content_list[-2].split(" ")[0] == "[Imagen]":
        content_list.pop(-1)
        content_list.pop(-1)
        article_end_corrector(content_list)
    
    if content_list[-1].split(" ")[0] == "[Cuerpo]" and ("Lea aquí" in content_list[-1] or \
                                                         "artículo" in content_list[-1] or \
                                                         "cobertura especial" in content_list[-1] or \
                                                         "nuestro mejor contenido" in content_list[-1]):
        content_list.pop(-1)
        article_end_corrector(content_list)

    if content_list[-1].split(" ")[0] == "[Imagen]":
        content_list.pop(-1)
        article_end_corrector(content_list)


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
            content.append("[Cuerpo] " + text.text.strip())
            link = element.find("a")
            if link is not None:
                content.append("[Enlace] " + link["href"])   

    article_end_corrector(content)

    # Tags
    tags_list = list()
    tags = soup.find("aside")
    if tags is not None:
        tags = tags.find_all("li")
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



news_links_path = Path("news_links.txt")
bbc_content_scraper_batch(news_links_path)

# TESTING
# URL = "https://www.bbc.com/mundo/noticias-59320917"
# article_id = URL.split("-")[-1]
# p = Path(f"bbc_news_content_scraped/{article_id}")
# p.mkdir(exist_ok=True)
# output_route = Path(f"bbc_news_content_scraped/{article_id}/{article_id}" + ".txt")
# bbc_content_scraper(URL, output_route)