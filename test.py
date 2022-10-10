import requests
from bs4 import BeautifulSoup

url = "https://www.bbc.com/mundo/noticias/2014/05/14052"
# url = "https://www.bbc.com/mundo/noticias/cluster_40_aniversario_golpe__estado_pinochet_chile"

page = requests.get(url)
# soup = BeautifulSoup(page.content, "html.parser")

if page.status_code == 404:
    print("Error")
else:
    print("OK!")