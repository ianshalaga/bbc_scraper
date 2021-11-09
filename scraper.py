import requests
from bs4 import BeautifulSoup
import subprocess

URL_base = "https://www.bbc.com"

exclude = ["/mundo/noticias-58984987", # Categoría: Medio ambiente
           "/mundo/noticias-36795069", # Categoría: Hay festival
           "/mundo/noticias-43826245", # Categoría: Centroamérica cuenta
           "/mundo/noticias-48908206"] # Categoría: BBC Extra

URL = "https://www.bbc.com/mundo/noticias-internacional-58956129"
page = requests.get(URL)

soup = BeautifulSoup(page.content, "html.parser")

results = soup.find(role="main")

elements = results.find_all("div", dir="ltr")

title = ""
author = list()
content = list()

for element in elements:
    # Título
    header = element.find("h1", id="content")
    if header is not None:
        title = header.text.strip() + "\n\n"

    # Autor/a
    person = element.find("li", role="listitem")
    if person is not None:
        author.append(person.text.strip() + "\n\n")

    # Imágenes
    # img = element.find("img")
    # if img is not None:
    #     link = img["src"]
    #     name = link.split("/")[-1]
    #     subprocess.run(["wget", "-c", "-O", name, link], check=True)

    subtitle = element.find("h2")
    text = element.find("p", dir="ltr")
    if subtitle is not None:
        content.append("\n\n" + subtitle.text.strip() + "\n\n")
    if text is not None:
        text2 = text.find("i")
        if text2 is None:
            content.append(text.text.strip() + " ")

with open("noticia.txt", "w") as f:
    f.write(title)
    f.write("Por: " + author[0])
    for element in content:
        f.write(element)

other_news = list()

results = soup.find("body")
links = results.find_all("a")

for link in links:
    if link is not None and \
    "noticias" in link["href"] and \
    link["href"].startswith("/mundo/noticias-") and \
    link["href"] not in exclude:
        print(URL_base + link["href"])
