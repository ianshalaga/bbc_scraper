import requests
from bs4 import BeautifulSoup
import subprocess



def flatten_body(content_list):
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



# URL = "https://www.bbc.com/mundo/noticias-internacional-59256983"
# URL = "https://www.bbc.com/mundo/noticias-59234155"
# URL = "https://www.bbc.com/mundo/noticias-america-latina-36466006"
# URL = "https://www.bbc.com/mundo/noticias-59234155"
# URL = "https://www.bbc.com/mundo/noticias-59244677"
# URL = "https://www.bbc.com/mundo/noticias-49966138"
# URL = "https://www.bbc.com/mundo/noticias-internacional-42883016"
URL = "https://www.bbc.com/mundo/noticias-59247492"

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
    # Título
    header = element.find("h1", id="content")
    if header is not None:
        title = header.text.strip()
        content.append("[Título] " + title)

    # Fecha
    pub_date = element.find_all("time", class_="bbc-14xtggo e4zesg50")
    if pub_date is not None and pub_date != []:
        date = pub_date[-1]["datetime"]
        content.append("[Fecha] " + date)

    # Autor/a
    person = element.find_all("li", role="listitem")
    if person is not None and person != [] and author_count == 0:
        for e in person:
            link = e.find("a")
            if link is None:
                author += e.text.strip() + ". "
        if author != "":
            content.append("[Autor] " + author)
        author_count += 1

    # Imágenes
    # img = element.find("img")
    # if img is not None:
    #     link = img["src"]
    #     name = link.split("/")[-1]
    #     subprocess.run(["wget", "-c", "-O", name, link], check=True)

    # img = element.find("figure")
    # if img is not None:
        # link = img["src"]
        # name = link.split("/")[-1]
        # subprocess.run(["wget", "-c", "-O", name, link], check=True)
        # content.append("\n\n")

    # Subtítulos
    subtitle = element.find("h2")
    text = element.find("p", dir="ltr")
    if subtitle is not None:
        content.append("[Subtítulo] " + subtitle.text.strip())

    # Imágenes y epígrafes
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

    # Cuerpos de texto
    if text is not None:
        content.append("[Cuerpo] " + text.text.strip())

flatten_list = flatten_body(content)

tags = soup.find("aside")
tags = tags.find_all("li")
tags_list = list()
for t in tags:
    tags_list.append(t.text.strip())

flatten_list.append("[Etiquetas] " + ", ".join(tags_list))

with open("noticia.txt", "w", encoding="utf8") as f:
    f.write("\n\n".join(flatten_list))
