from cv2 import detail_MatchesInfo
import assets_for_video_generator as assets
import subprocess
from termcolor import colored
import logging
import os
import shutil
import csv
import re



def video_generator(article_scraped_path, video_default_assets_folfer, videos_to_upload_path, article_id, width_target, height_target, fps):
    fail = False
    # Assests generation
    have_assets = assets.assets_for_video_generator(article_scraped_path, video_default_assets_folfer, videos_to_upload_path, article_id, width_target, height_target, fps)
    if have_assets:
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
            fail = True
            return fail

        # Assets cleaning
        shutil.rmtree(assets_folder) # Assets cleaning
        source_video_path = os.path.join(article_scraped_path, article_id + ".mp4")
        source_description_path = os.path.join(article_scraped_path, article_id + "_description.txt")
        shutil.move(source_video_path, videos_to_upload_path)
        shutil.move(source_description_path, videos_to_upload_path)
    else:
        fail = True
        print(colored(f"El artículo {article_id} no contiene imágenes.", "red"))

    return fail


def video_generator_batch(total_ids_path,
                          videos_ids_path,
                          article_scraped_folder,
                          video_default_assets_folfer,
                          videos_to_upload_path,
                          width_target,
                          height_target,
                          fps,
                          ban_keywords_list,
                          excluded_videos_path):
    videos_ids_list = list()
    with open(videos_ids_path, "r", encoding="utf8") as f:
        videos_ids_list = f.read().split("\n")

    excluded_videos_list = list()
    with open(excluded_videos_path, "r", encoding="utf8") as f:
        excluded_videos_list = f.read().split("\n")

    with open(total_ids_path, encoding="utf8") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        for row in csv_reader:
            article_id = row[0]
            if article_id not in videos_ids_list:
                if article_id not in excluded_videos_list:
                    ban = False
                    for ban_keyword in ban_keywords_list:
                        if bool(re.search(ban_keyword, " ".join(row[1:]))):
                            ban = True
                            break
                    if ban == True:
                        print(colored(f"El artículo {article_id} fue excluído por poseer palabras clave restringidas.", "red"))
                        continue
                    else:
                        article_scraped_path = os.path.join(article_scraped_folder, article_id)
                        fail = video_generator(article_scraped_path, video_default_assets_folfer, videos_to_upload_path, article_id, width_target, height_target, fps)
                        if not(fail):
                            videos_ids_list.append(article_id)
                            videos_ids_list.sort()
                        with open(videos_ids_path, "w", encoding="utf8") as f:
                            f.write("\n".join(videos_ids_list))
                else:
                    print(colored(f"El artículo {article_id} se encuentra excluído.", "red"))    
            else:
                print(colored(f"El artículo {article_id} ya tiene video.", "green"))

###

total_ids_path = "news_id_tags.csv"
videos_ids_path = "news_videos.txt"
article_scraped_folder = "bbc_news_content_scraped"
video_default_assets_folfer = "video_default_assets"
videos_to_upload_path = "videos_to_upload"
width_target = 1920
height_target = 1080
fps = 60
ban_keywords_list = ["coronavirus"]
excluded_videos_path = "excluded_videos.txt"

video_generator_batch(total_ids_path,
                      videos_ids_path,
                      article_scraped_folder,
                      video_default_assets_folfer,
                      videos_to_upload_path,
                      width_target,
                      height_target,
                      fps,
                      ban_keywords_list,excluded_videos_path)


''' TESTING '''
# article_id = str(36491140)
# article_scraped_path = os.path.join(article_scraped_folder, article_id)
# video_generator(article_scraped_path, video_default_assets_folfer, videos_to_upload_path, article_id, width_target, height_target, fps)
