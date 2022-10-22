import requests
from bs4 import BeautifulSoup

# url = "https://www.bbc.com/mundo/noticias/2014/05/14052"
# url = "https://www.bbc.com/mundo/noticias/cluster_40_aniversario_golpe__estado_pinochet_chile"

url1 = "https://www.bbc.com/mundo/noticias/2010/10/100930_ciencia_panama_canal_arqueologia_mes"
url2 = "https://www.bbc.com/mundo/noticias/2010/10/100930_ciencia_panama_canal_arqueologia_mes.shtml"

page = requests.get(url2)
# soup = BeautifulSoup(page.content, "html.parser")

print(page.url)

# if page.status_code == 404:
#     print("Error")
# else:
#     print("OK!")