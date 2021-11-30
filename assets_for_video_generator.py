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
import re
import random



def get_wave_duration(wave_path):
    with contextlib.closing(wave.open(wave_path, "r")) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        duration = math.ceil(frames / float(rate)) + 0.5
        return duration


def allowed_voices(article_scraped_path):
    # Voices lists
    voices_fail_romans_list = ["IVONA 2 Conchita",
                               "IVONA 2 Enrique",
                               "IVONA 2 Miguel",
                               "IVONA 2 Penélope",
                               "Microsoft Sabina Desktop",
                               "Microsoft Raul Mobile"
    ]
    voices_fail_point_numbers_list = ["IVONA 2 Miguel",
                                      "IVONA 2 Penélope",
                                      "Microsoft Sabina Desktop"
    ]
    voices_ok_list = ["Loquendo Carlos",
                      "Loquendo Carmen",
                      "Loquendo Diego",
                      "Loquendo Esperanza",
                      "Loquendo Francisca",
                      "Loquendo Jorge",
                      "Loquendo Juan",
                      "Loquendo Leonor",
                      "Loquendo Soledad",
                      "Loquendo Ximena",
                      "Microsoft Helena Desktop",
                      "Microsoft Laura Mobile",
                      "Microsoft Pablo Mobile"
    ]

    allowed_voices_list = list()
    content_list = list()
    with open(article_scraped_path, "r", encoding="utf8") as f:
        content_list = f.read().split("\n\n")
    fails_roman = False
    fails_numbers = False
    for sentense in content_list:
        sentense_split = sentense.split(" ")[1:]
        for word in sentense_split:
            word_stripped = word.strip(".,:;")
            if bool(re.search(r"^M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$", word_stripped)):
                fails_roman = True
                break
            if bool(re.search(r"[+-]?([0-9]*[.])[0-9]+", word_stripped)):
                fails_numbers = True
                break
    
    if fails_roman and fails_numbers:
        allowed_voices_list = voices_ok_list
    elif fails_roman and not fails_numbers:
        allowed_voices_list = voices_ok_list + voices_fail_point_numbers_list
    elif not fails_roman and fails_numbers:
        allowed_voices_list = voices_ok_list + voices_fail_romans_list
    else:
        allowed_voices_list = voices_ok_list + voices_fail_romans_list + voices_fail_point_numbers_list
    
    return allowed_voices_list


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

    images_processed_text_folder = Path(os.path.join(assets_folder, "images_processed_text"))
    images_processed_text_folder.mkdir(exist_ok=True)

    text_folder = Path(os.path.join(assets_folder, "text_content"))
    text_folder.mkdir(exist_ok=True)

    audio_folder = Path(os.path.join(assets_folder, "audio_files"))
    audio_folder.mkdir(exist_ok=True)    

    specs_dict = dict()
    specs_file_path = os.path.join(video_folder, "specs.json5")
    video_file_path = os.path.join(article_scraped_folder, "video", article_id + ".mp4")
    video_font_path = os.path.join(video_default_assets_folfer, "fonts", "AveriaSerif-Bold.ttf")
    background_audio_path = list(Path(os.path.join(video_default_assets_folfer, "audio")).iterdir())
    random.shuffle(background_audio_path)
    specs_dict["outPath"] = video_file_path
    specs_dict["width"] = width_target
    specs_dict["height"] = height_target
    specs_dict["fps"] = fps
    specs_dict["defaults"] = {"layer": {"fontPath": video_font_path}}

    content_list  = list()
    article_scraped_path = os.path.join(article_scraped_folder, article_id + ".txt")
    with open(article_scraped_path, "r", encoding="utf8") as f:
        content_list = f.read().split("\n\n")

    c = 0
    current_background = ""
    current_background_caption = ""
    allowed_voices_list = allowed_voices(article_scraped_path)
    article_voice = random.choice(allowed_voices_list)
    current_image_path = ""
    for e in content_list:
        c += 1
        content_tag = e.split(" ")[0]
        content_body = " ".join(e.split(" ")[1:])

        if content_tag == "[Título]": # File for title
            text_name = str(c) + "_title"
            title_path = os.path.join(text_folder, text_name + ".txt")
            with open(title_path, "w", encoding="utf8") as f:
                f.write(content_body)
            wave_path = os.path.join(audio_folder, text_name + ".wav")
            try:
                subprocess.run(["balcon", # Command line Balabolka
                                "-n", # Voice name
                                article_voice, # "IVONA 2 Enrique",
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

            specs_dict["clips"] = [
                {
                    "duration": get_wave_duration(wave_path) + 2,
                    "layers": [
                        {
                            "type": "title-background",
                            "text": content_body,
                            "background": {
                                "type": "radial-gradient"
                            }
                        },
                        {
                            "type": "detached-audio",
                            "path": wave_path,
                            "start": 2
                        }
                    ]
                }
            ]

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
                                article_voice, # "IVONA 2 Enrique",
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
                            "path": current_background_caption,
                            "zoomDirection": "null"
                        },
                        {
                            "type": "subtitle",
                            "text": content_body
                        },
                        {
                            "type": "detached-audio",
                            "path": wave_path,
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
                            "path": current_background,
                            "zoomDirection": "null"
                        },
                        {
                            "type": "news-title",
                            "text": content_body
                        }
                    ]
                }
            )

        if content_tag == "[Epígrafe]": # Files for captions
            caption_path = os.path.join(text_folder, str(c) + "_caption.txt")
            with open(caption_path, "w", encoding="utf8") as f:
                f.write(content_body)
            images_processed_text_path = os.path.join(images_processed_text_folder, Path(current_image_path).name)    
            ip.put_caption_on_image_processed(current_image_path, images_processed_text_path, content_body, video_font_path)

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
                current_image_path = image_processed_path
                ip.image_for_video_generator(image_path, image_processed_path, width_target, height_target)
                image_processed_text_path = os.path.join(images_processed_text_folder, image_name)
                ip.image_for_video_generator(image_path, image_processed_text_path, width_target, height_target)
            except subprocess.CalledProcessError as ex:
                print(colored("Error descargando.", "red"))
                logging.log(logging.ERROR, "Error descargando:", ex)
            current_background = image_processed_path
            current_background_caption = image_processed_text_path

    specs_dict["clips"].append(
        {
            "duration": 20.5,
            "layers": [{"type": "radial-gradient"}]
        }
    )

    specs_dict["loopAudio"] = "true"

    audiotracks_list = list()
    for at in background_audio_path:
        audiotracks_list.append({"path": str(at), "mixVolume": 0.1})
    specs_dict["audioTracks"] = audiotracks_list

    # specs_dict["audioTracks"] = [
    #     {
    #         "path": str(random.choice(background_audio_path)),
    #         "mixVolume": 0.1
    #     }
    # ]

    specs_dict["audioNorm"] = {
        "enable": "true",
        "maxGain": 40
    }

    # Debugging
    # specs_dict["fast"] = "true"

    with open(specs_file_path, "w", encoding="utf8") as f:
        json.dump(specs_dict, f)



URL = "https://www.bbc.com/mundo/noticias-59320917"

article_id = URL.split("-")[-1]

article_scraped_folder = Path(f"bbc_news_content_scraped/{article_id}")
video_default_assets_folfer = Path("video_default_assets")

width_target = 1920
height_target = 1080
fps = 60

assets_for_video_generator(article_scraped_folder, video_default_assets_folfer, article_id, width_target, height_target, fps)
