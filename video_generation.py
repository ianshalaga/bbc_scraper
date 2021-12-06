from cv2 import detail_MatchesInfo
import assets_for_video_generator as assets
import subprocess
from termcolor import colored
import logging
import os
import shutil
import csv
import re


def video_generator(article_scraped_path, video_default_assets_folfer, article_id, width_target, height_target, fps):
    # Assests generation
    assets.assets_for_video_generator(article_scraped_path, video_default_assets_folfer, article_id, width_target, height_target, fps)

    # Video generation
    assets_folder = os.path.join(article_scraped_path, "assets")
    specs_path = os.path.join(assets_folder, "specs.json5")
    try:
        subprocess.run(["editly", # Command line video editor Editly
                        specs_path
                        ], shell=True)
        print(colored("Generado:", "green"), article_id + ".mp4")
    except subprocess.CalledProcessError as ex:
        print(colored("Error al generar el archivo de video.", "red"))
        logging.log(logging.ERROR, "Error al generar el archivo de video:", ex)
        return
    
    # Assets cleaning
    try:
        shutil.rmtree(assets_folder)
    except OSError as e:
        print(f'Error: {assets_folder} : {e.strerror}')


def video_generator_batch(total_ids_path,
                          videos_ids_path,
                          article_scraped_folder,
                          video_default_assets_folfer,
                          width_target,
                          height_target,
                          fps,
                          ban_keywords_list):
    videos_ids_list = list()
    with open(videos_ids_path, "r", encoding="utf8") as f:
        videos_ids_list = f.read().split("\n")

    with open(total_ids_path, encoding="utf8") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        for row in csv_reader:
            article_id = row[0]
            if article_id not in videos_ids_list:
                ban = False
                for ban_keyword in ban_keywords_list:
                    if bool(re.search(ban_keyword, " ".join(row[1:]))):
                        ban = True
                        break
                if ban == True:
                    print(f"El artículo {article_id} fue excluído por poseer palabras clave restringidas.")
                    continue
                else:
                    article_scraped_path = os.path.join(article_scraped_folder, article_id)
                    video_generator(article_scraped_path, video_default_assets_folfer, article_id, width_target, height_target, fps)
                    with open(videos_ids_path, "a", encoding="utf8") as f:
                        f.write(article_id + "\n")
            else:
                print(f"El artículo {article_id} ya tiene video.")

###

total_ids_path = "news_id_tags.csv"
videos_ids_path = "news_videos.txt"
article_scraped_folder = "bbc_news_content_scraped"
video_default_assets_folfer = "video_default_assets"
width_target = 1920
height_target = 1080
fps = 60
ban_keywords_list = ["coronavirus"]

video_generator_batch(total_ids_path,
                      videos_ids_path,
                      article_scraped_folder,
                      video_default_assets_folfer,
                      width_target,
                      height_target,
                      fps,
                      ban_keywords_list)