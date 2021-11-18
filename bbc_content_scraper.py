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
        caption = element.find("figure")
        if caption is not None:
            link = caption.find("img")
            caption = caption.find("figcaption")
            if caption is not None:
                caption = caption.find("p")
                if caption is not None:
                    content.append("[Imagen] " + link["src"])
                    content.append("[Epígrafe] " + caption.text.strip())
            else:
                content.append("[Imagen] " + link["src"])

        # Text bodies
        if text is not None:
            content.append("[Cuerpo] " + text.text.strip())

    flatten_list = flatten_body(content)

    tags = soup.find("aside")
    tags = tags.find_all("li")
    tags_list = list()
    for t in tags:
        tags_list.append(t.text.strip())

    flatten_list.append("[Etiquetas] " + ", ".join(tags_list))

    with open(output_route, "w", encoding="utf8") as f:
        f.write("\n\n".join(flatten_list))



URL = "https://www.bbc.com/mundo/deportes-59326089"

article_id = URL.split("-")[-1]

p = Path(f"bbc_news_content_scraped/{article_id}")
p.mkdir(exist_ok=True)

output_route = os.path.join(p, article_id + ".txt")

bbc_content_scraper(URL, output_route)