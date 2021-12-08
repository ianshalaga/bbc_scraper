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
from pydub import AudioSegment
import urllib.parse as urlp



def audio_track_generator(audio_tracks_path, output_song_path):
    time_limit = 2700 # 45 minutes
    p = Path(audio_tracks_path)
    audio_genders = list(p.iterdir())
    audios_selected = random.choice(audio_genders)
    print(f"Género seleccionado: {audios_selected.name}")
    audios_selected_list = list(audios_selected.iterdir())

    print("Aleatorizando...")
    random.shuffle(audios_selected_list)

    songs_list = list()
    time_count = 0
    for song_path in audios_selected_list:
        if time_count >= time_limit:
            break
        else:
            time_count += get_wave_duration(str(song_path))
            songs_list.append(AudioSegment.from_file(song_path, format="wav"))
            print(f"Añadida: {song_path.name}")
    
    # Merge songs
    song = songs_list[0]
    for i in range(1,len(songs_list)):
        print(f"Uniendo: {i}/{len(songs_list)-1}")
        song += songs_list[i]

    print("Guardando archivo de audio...")
    song.export(output_song_path, format="wav")


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

    song_folder = Path(os.path.join(assets_folder, "audio_song"))
    song_folder.mkdir(exist_ok=True)

    specs_dict = dict()
    specs_file_path = os.path.join(assets_folder, "specs.json5")
    video_file_path = os.path.join(article_scraped_folder, article_id + ".mp4")
    video_font_bodies_path = os.path.join(video_default_assets_folfer, "fonts", "AveriaSerif-Bold.ttf")
    video_font_titles_path = os.path.join(video_default_assets_folfer, "fonts", "LTAsus-Heavy.ttf")
    description_file_path = os.path.join(article_scraped_folder, article_id + "_description.txt")
    
    default_audios_folder = os.path.join(video_default_assets_folfer, "audio")
    song_path = os.path.join(song_folder, "song.wav")
    audio_track_generator(default_audios_folder, song_path)

    specs_dict["outPath"] = video_file_path
    specs_dict["width"] = width_target
    specs_dict["height"] = height_target
    specs_dict["fps"] = fps
    specs_dict["defaults"] = {"layer": {"fontPath": video_font_bodies_path}}

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

            # For json5 file
            specs_dict["clips"] = [
                {
                    "duration": get_wave_duration(wave_path) + 2,
                    "layers": [
                        {
                            "type": "title-background",
                            "text": content_body,
                            "background": {
                                "type": "radial-gradient"
                            },
                            "fontPath": video_font_titles_path
                        },
                        {
                            "type": "detached-audio",
                            "path": wave_path,
                            "start": 2
                        }
                    ]
                }
            ]

            # For description file
            with open(description_file_path, "w", encoding="utf8") as f:
                f.write(content_body + "\n")

        if content_tag == "[Autor]": # File for author
            author_path = os.path.join(text_folder, str(c) + "_author.txt")
            with open(author_path, "w", encoding="utf8") as f:
                f.write(content_body)

            # For json5 file
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
            
            # For json5 file
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
            
            # For json5 file
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

            # For json5 file
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
                            "type": "subtitle",
                            "text": content_body,
                            "fontPath": video_font_titles_path,
                            "textColor": "#ffff00"
                        }
                    ]
                }
            )

        if content_tag == "[Epígrafe]": # Files for captions
            caption_path = os.path.join(text_folder, str(c) + "_caption.txt")
            with open(caption_path, "w", encoding="utf8") as f:
                f.write(content_body)
            images_processed_text_path = os.path.join(images_processed_text_folder, Path(current_image_path).name)    
            ip.put_caption_on_image_processed(current_image_path, images_processed_text_path, content_body, video_font_bodies_path)

        if content_tag == "[Imagen]":
            print(f"Descargargo: {content_body}")
            image_ext = content_body.split(".")[-1]
            # image_ext = "jpg"
            image_name = str(c) + "_image." + image_ext
            image_path = os.path.join(images_folder, image_name)
            try:
                # Images downloader
                subprocess.run(["wget",
                                "-c", "-O",
                                image_path, content_body.split("://")[0] + "://" + urlp.quote(content_body.split("://")[1]),
                                "--no-check-certificate"], check=True)
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

        # For description file
        if content_tag == "[Etiquetas]":
            with open(description_file_path, "a", encoding="utf8") as f:
                f.write(content_body + "\n")

        if content_tag == "[Enlace]":
            with open(description_file_path, "a", encoding="utf8") as f:
                f.write("Enlace: " + content_body + "\n")

        if content_tag == "[Fuente]":
            with open(description_file_path, "a", encoding="utf8") as f:
                f.write("Fuente: " + content_body)

    # For json5 file    
    specs_dict["clips"].append(
        {
            "duration": 20.5,
            "layers": [
                {
                    "type": "image",
                    "path": current_background,
                    "zoomDirection": "null"
                }
            ]
        }
    )

    specs_dict["loopAudio"] = "true"

    specs_dict["audioTracks"] = [
        {
            "path": song_path,
            "mixVolume": 0.1
        }
    ]

    specs_dict["audioNorm"] = {
        "enable": "true",
        "maxGain": 40
    }

    # Debugging
    # specs_dict["fast"] = "true"

    with open(specs_file_path, "w", encoding="utf8") as f:
        json.dump(specs_dict, f)



# URL = "https://www.bbc.com/mundo/noticias-59432415"

# article_id = URL.split("-")[-1]

# article_scraped_folder = Path(f"bbc_news_content_scraped/{article_id}")
# video_default_assets_folfer = Path("video_default_assets")

# width_target = 1920
# height_target = 1080
# fps = 60

# assets_for_video_generator(article_scraped_folder, video_default_assets_folfer, article_id, width_target, height_target, fps)
