import subprocess
import os


content_list = list()
with open("noticia.txt", "r", encoding="utf8") as f:
    content_list = f.read().split("\n\n")

c = 0
bodies_list = list()
for e in content_list:
    image_link_list = e.split(" ")
    if image_link_list[0] == "[Imagen]":
        print(image_link_list[1])
        c += 1
        name = str(c) + "." + image_link_list[1].split(".")[-1]
        ruta = os.path.join("noticia", name)
        subprocess.run(["wget", "-c", "-O", ruta, image_link_list[1], "--no-check-certificate"], check=True)
    if image_link_list[0] == "[Cuerpo]":
        bodies_list.append(" ".join(image_link_list[1:]))

with open("noticia/noticia_bodies.txt", "w", encoding="utf8") as f:
    f.write("\n\n\n".join(bodies_list))