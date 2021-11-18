import subprocess
import os
from pathlib import Path
import logging
from termcolor import colored
import image_processing as ip



def assets_for_video_generator(article_scraped_folder, article_id, width_target, height_target):
    assets_folder = Path(os.path.join(article_scraped_folder, "assets"))
    assets_folder.mkdir(exist_ok=True)

    print(article_scraped_folder)

    content_list  = list()
    article_scraped_route = os.path.join(article_scraped_folder, article_id + ".txt")
    with open(article_scraped_route, "r", encoding="utf8") as f:
        content_list = f.read().split("\n\n")

    c = 0
    bodies_list = list()
    images_folder = Path(os.path.join(assets_folder, "images_downloaded"))
    for e in content_list:
        image_link_list = e.split(" ")
        if image_link_list[0] == "[Imagen]": # Images downloader
            images_folder.mkdir(exist_ok=True)

            c += 1
            image_name = str(c) + "." + image_link_list[1].split(".")[-1]
            image_path = os.path.join(images_folder, image_name)

            try:
                subprocess.run(["wget", "-c", "-O", image_path, image_link_list[1], "--no-check-certificate"], check=True)
                print(colored("Guardado", "green"), image_name)
            except subprocess.CalledProcessError as ex:
                print(colored("Error descargando.", "red"))
                logging.log(logging.ERROR, "Error descargando:", ex)
                
        if image_link_list[0] == "[Cuerpo]": # Text content
            bodies_list.append(" ".join(image_link_list[1:]))

    # Text content
    text_path = os.path.join(assets_folder, "text_content.txt")
    with open(text_path, "w", encoding="utf8") as f:
        f.write("\n\n\n".join(bodies_list))

    # Images processing
    images_processed_folder = Path(os.path.join(assets_folder, "images_processed"))
    images_processed_folder.mkdir(exist_ok=True)
    for image_path in images_folder.iterdir():
        image_processed_path = os.path.join(images_processed_folder, image_path.name)
        ip.image_for_video_generator(image_path, image_processed_path, width_target, height_target)



URL = "https://www.bbc.com/mundo/noticias-internacional-58768373"

article_id = URL.split("-")[-1]

article_scraped_folder = Path(f"bbc_news_content_scraped/{article_id}")

width_target = 1920
height_target = 1080

assets_for_video_generator(article_scraped_folder, article_id, width_target, height_target)