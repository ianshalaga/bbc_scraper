import subprocess
import os
import logging
import json
import image_processing as ip
from pathlib import Path
from termcolor import colored
import wave
import contextlib
import math



def get_wave_duration(wave_path):
    with contextlib.closing(wave.open(wave_path, "r")) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        duration = math.ceil(frames / float(rate)) + 0.5
        return duration


def assets_for_video_generator(article_scraped_folder,
                               video_default_assets_folfer,
                               article_id,
                               width_target,
                               height_target,
                               fps):
                               
    assets_folder = Path(os.path.join(article_scraped_folder, "assets"))
    assets_folder.mkdir(exist_ok=True)

    video_folder = Path(os.path.join(article_scraped_folder, "video"))
    video_folder.mkdir(exist_ok=True)

    images_folder = Path(os.path.join(assets_folder, "images_downloaded"))
    images_folder.mkdir(exist_ok=True)

    images_processed_folder = Path(os.path.join(assets_folder, "images_processed"))
    images_processed_folder.mkdir(exist_ok=True)

    text_folder = Path(os.path.join(assets_folder, "text_content"))
    text_folder.mkdir(exist_ok=True)

    audio_folder = Path(os.path.join(assets_folder, "audio_files"))
    audio_folder.mkdir(exist_ok=True)    

    specs_dict = dict()
    specs_file_path = os.path.join(video_folder, "specs.json5")
    video_file_path = os.path.join(article_scraped_folder, "video", article_id + ".mp4")
    video_font_path = os.path.join(video_default_assets_folfer, "fonts", "AveriaSerif-Bold.ttf")
    background_audio_path = os.path.join(video_default_assets_folfer, "audio", "Light Expanse - Unicorn Heads.mp3")
    specs_dict["outPath"] = video_file_path
    specs_dict["width"] = width_target
    specs_dict["height"] = height_target
    specs_dict["fps"] = fps
    specs_dict["defaults"] = {"layer": {"fontPath": video_font_path}}
    specs_dict["clips"] = [{}]
    specs_dict["clips"][0]["duration"] = 10
    specs_dict["clips"][0]["layers"] = []
    # specs_dict["clips"].append({})

    content_list  = list()
    article_scraped_route = os.path.join(article_scraped_folder, article_id + ".txt")
    with open(article_scraped_route, "r", encoding="utf8") as f:
        content_list = f.read().split("\n\n")

    c = 0
    actual_background = ""
    actual_caption = ""
    for e in content_list:
        c += 1
        content_tag = e.split(" ")[0]
        content_body = " ".join(e.split(" ")[1:])

        if content_tag == "[Título]": # File for title
            title_path = os.path.join(text_folder, str(c) + "_title.txt")
            with open(title_path, "w", encoding="utf8") as f:
                f.write(content_body)
            wave_path = os.path.join(audio_folder, text_name + ".wav")
            try:
                subprocess.run(["balcon", # Command line Balabolka
                                "-n", # Voice name
                                "IVONA 2 Enrique",
                                "-f",
                                title_path,
                                "-w", # Wave file
                                wave_path,
                                "-enc", # Encoding
                                "utf8"
                                ], check=True)
                print(colored("Generado:", "green"), text_name + ".wav")
            except subprocess.CalledProcessError as ex:
                print(colored("Error al generar el archivo de audio.", "red"))
                logging.log(logging.ERROR, "Error al generar el archivo de audio:", ex)

            specs_dict["clips"][0]["layers"].append(
                {
                    "type": "title-background",
                    "text": content_body,
                    "background": {
                        "type": "radial-gradient"
                    }
                }
            )

        if content_tag == "[Autor]": # File for author
            author_path = os.path.join(text_folder, str(c) + "_author.txt")
            with open(author_path, "w", encoding="utf8") as f:
                f.write(content_body)
    
            specs_dict["clips"][0]["layers"].append(
                {
                    "type": "slide-in-text",
                    "text": content_body,
                    "position": "top-left",
                    "fontSize": "0.02"
                }
            )

        if content_tag == "[Fecha]": # File for date
            date_path = os.path.join(text_folder, str(c) + "_date.txt")
            with open(date_path, "w", encoding="utf8") as f:
                f.write(content_body)
            
            specs_dict["clips"][0]["layers"].append(
                {
                    "type": "slide-in-text",
                    "text": content_body,
                    "position": "bottom-right",
                    "fontSize": "0.02"
                }
            )

        if content_tag == "[Cuerpo]": # Files for text bodies
            text_name = str(c) + "_body"
            text_path = os.path.join(text_folder, text_name + ".txt")
            with open(text_path, "w", encoding="utf8") as f:
                f.write(content_body)
            print(f"Generando audio para {text_name}")
            wave_path = os.path.join(audio_folder, text_name + ".wav")
            try:
                subprocess.run(["balcon", # Command line Balabolka
                                "-n", # Voice name
                                "IVONA 2 Enrique",
                                "-f",
                                text_path,
                                "-w", # Wave file
                                wave_path,
                                "-enc", # Encoding
                                "utf8"
                                ], check=True)
                print(colored("Generado:", "green"), text_name + ".wav")
            except subprocess.CalledProcessError as ex:
                print(colored("Error al generar el archivo de audio.", "red"))
                logging.log(logging.ERROR, "Error al generar el archivo de audio:", ex)
            
            specs_dict["clips"].append(
                {
                    "duration": get_wave_duration(wave_path),
                    "transition": {
                        "name": "dummy"
                    },
                    "layers": [
                        {
                            "type": "image",
                            "path": actual_background,
                            "zoomDirection": "null"
                        },
                        {
                            "type": "subtitle",
                            "text": content_body
                        },
                        {
                            "type": "detached-audio",
                            "path": wave_path,
                        },
                        {
                            "type": "title",
                            "text": actual_caption,
                            "position": "top-left"
                        }
                    ]
                }
            )
            

        if content_tag == "[Subtítulo]": # Files for subtitles
            subtitle_path = os.path.join(text_folder, str(c) + "_subtitle.txt")
            with open(subtitle_path, "w", encoding="utf8") as f:
                f.write(content_body)
        
            specs_dict["clips"].append(
                {
                    "duration": 4,
                    "layers": [
                        {
                            "type": "image",
                            "path": actual_background,
                            "zoomDirection": "null"
                        },
                        {
                            "type": "news-title",
                            "text": content_body
                        },
                    ]
                }
            )

        if content_tag == "[Epígrafe]": # Files for captions
            caption_path = os.path.join(text_folder, str(c) + "_caption.txt")
            with open(caption_path, "w", encoding="utf8") as f:
                f.write(content_body)
            actual_caption = content_body

        if content_tag == "[Imagen]":
            print(f"Descargargo: {content_body}")
            image_ext = content_body.split(".")[-1]
            image_name = str(c) + "_image." + image_ext
            image_path = os.path.join(images_folder, image_name)
            try:
                # Images downloader
                subprocess.run(["wget", "-c", "-O", image_path, content_body, "--no-check-certificate"], check=True)
                print(colored("Guardado", "green"), image_name)
                # Images processing
                image_processed_path = os.path.join(images_processed_folder, image_name)
                ip.image_for_video_generator(image_path, image_processed_path, width_target, height_target)
            except subprocess.CalledProcessError as ex:
                print(colored("Error descargando.", "red"))
                logging.log(logging.ERROR, "Error descargando:", ex)
            actual_background = image_processed_path

    specs_dict["clips"].append(
        {
            "duration": 20.5,
            "layers": [{"type": "radial-gradient"}]
        }
    )

    specs_dict["loopAudio"] = "true"

    specs_dict["audioTracks"] = [
        {
            "path": background_audio_path,
            "mixVolume": 0.15
        }
    ]

    specs_dict["audioNorm"] = {
        "enable": "true"
    }

    # Debugging
    specs_dict["fast"] = "true"

    with open(specs_file_path, "w", encoding="utf8") as f:
        json.dump(specs_dict, f)


    




URL = "https://www.bbc.com/mundo/noticias-internacional-59410385"

article_id = URL.split("-")[-1]

article_scraped_folder = Path(f"bbc_news_content_scraped/{article_id}")
video_default_assets_folfer = Path("video_default_assets")

width_target = 1920
height_target = 1080
fps = 60

assets_for_video_generator(article_scraped_folder, video_default_assets_folfer, article_id, width_target, height_target, fps)


# wave_path = "bbc_news_content_scraped/59276948/assets/audio_files/6_body.wav"
# duration = get_wave_duration(wave_path)
# print(duration)