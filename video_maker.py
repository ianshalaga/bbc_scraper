import LÑdb as db
from pathlib import Path
import re
import os
import random
from termcolor import colored
from pydub import AudioSegment
import math
import wave
import contextlib
import subprocess
import logging
from PIL import Image, ImageFont, ImageDraw # Put text on image
import urllib.parse as urlp
import cv2
from fractions import Fraction # Fractions manipulation
import json
import shutil


SR_ENGINE_PATH = "Real-ESRGAN/Real-ESRGAN.bat"


def super_resolution(image_path, SR_ENGINE_PATH):
    current_path = os.getcwd() # Absolute path needed
    sr_engine = os.path.join(current_path, SR_ENGINE_PATH)
    image_absolute_path = os.path.join(current_path, image_path)
    subprocess_list = [sr_engine, image_absolute_path]
    subprocess.run(subprocess_list)


def image_for_video_generator(image_path, # Original downloaded image path
                              images_processed_path, # Image processed for video path
                              width_target, # Video resolution: width
                              height_target): # Video resolution: height
    images_processed_path = ".".join(images_processed_path.split(".")[:-1]) + ".jpg" # Force jpg extension for output image

    image = cv2.imread(str(image_path)) # Read input image

    image_jpg_path = ".".join(image_path.split(".")[:-1]) + ".jpg" # Force jpg extension for input image
    cv2.imwrite(str(image_jpg_path), image) # Save input image as jpg

    height, width, _ = image.shape

    if height < height_target or width < width_target:
        scale_sr_factor = 4
        scales_width = math.ceil((width_target / width) / scale_sr_factor)
        scales_height = math.ceil((height_target / height) / scale_sr_factor)
        scales_number = max([scales_width, scales_height])
        for _ in range(scales_number):
            super_resolution(image_jpg_path, SR_ENGINE_PATH)

    image = cv2.imread(str(image_jpg_path)) # Read input image
    height, width, _ = image.shape

    aspect_ratio = Fraction(width_target, height_target)
    width_target_aspect_ratio = aspect_ratio.numerator
    height_target_aspect_ratio = aspect_ratio.denominator

    # Background generation
    if height > width:
        height_scaled = int(width*height_target_aspect_ratio/width_target_aspect_ratio)
        start = int((height-height_scaled)/2)
        background = image[start:start+height_scaled,:]
    else:
        width_scaled = int(height*width_target_aspect_ratio/height_target_aspect_ratio)
        start = int((width-width_scaled)/2)
        background = image[:,start:start+width_scaled]

    background = cv2.resize(background, [width_target, height_target])
    background = cv2.GaussianBlur(background, [int(height_target/10)+1, int(height_target/10)+1], 0, 0)

    # Output generation
    if width_target >= width:
        if height_target >= height:
            width_start = int((width_target-width)/2)
            height_start = int((height_target-height)/2)
            background[height_start:height_start+height, width_start:width_start+width] = image
        else:
            width_scaled = int(width*height_target/height)
            width_start = int((width_target-width_scaled)/2)
            background[:, width_start:width_start+width_scaled] = cv2.resize(image, [width_scaled, height_target])
    else:
        if height_target >= height:
            height_scaled = int(height*width_target/width)
            height_start = int((height_target-height_scaled)/2)
            background[height_start:height_start+height_scaled, :] = cv2.resize(image, [width_target, height_scaled])
        else:
            if height > width:
                width_scaled = int(width*height_target/height)
                width_start = int((width_target-width_scaled)/2)
                background[:, width_start:width_start+width_scaled] = cv2.resize(image, [width_scaled, height_target])
            else:
                height_scaled = int(height*width_target/width)
                height_start = int((height_target-height_scaled)/2)
                background[height_start:height_start+height_scaled, :] = cv2.resize(image, [width_target, height_scaled])

    # Display image for testing
    # cv2.imshow("Imagen", background)
    # cv2.waitKey(0) # waits until a key is pressed
    # cv2.destroyAllWindows() # destroys the window showing image
    
    cv2.imwrite(str(images_processed_path), background)


def put_caption_on_image_processed(images_processed_path, images_processed_text_path, text_caption, font_path):
    images_processed_path = ".".join(images_processed_path.split(".")[:-1]) + ".jpg" # Force jpg extension
    words_list = text_caption.split(" ")
    c = 0
    string_list = list()
    text_list = list()

    for word in words_list:
        if c == 9:
            string_list.append(word)
            text_list.append(" ".join(string_list))
            string_list = list()
            c = 0
        else:
            string_list.append(word)
            c += 1
    
    if c != 0:
        text_list.append(" ".join(string_list))
    
    image_processed = Image.open(images_processed_path)
    font = ImageFont.truetype(font_path, 50)
    y = 15
    image = image_processed.copy()
    image_draw = ImageDraw.Draw(image)
    image_draw.rectangle([0,0, image_processed.width, 2*y+len(text_list)*50], 0)
    image_blended = Image.blend(image_processed, image, 0.8)
    image_draw = ImageDraw.Draw(image_blended)

    for i in range(len(text_list)):
        image_draw.text((15,y+i*50), text_list[i], (230, 230, 0), font=font, align='center')

    image_blended.save(images_processed_text_path)


def allowed_voices(news_content_string):
    '''
    Determine the list of voices that can be used based on the content of the article.
    '''
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
    content_list = news_content_string.split("\n\n")

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


def get_wave_duration(wave_path):
    '''
    Get the duration of a wave audio file.
    '''
    with contextlib.closing(wave.open(wave_path, "r")) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        duration = math.ceil(frames / float(rate)) + 0.5
        return duration


def audio_track_generator(audio_tracks_path, output_song_path):
    '''
    Generate a random audio track for background music.
    '''
    time_limit = 2700 # 45 minutes
    p = Path(audio_tracks_path)
    audio_genders = list(p.iterdir())
    audios_selected = random.choice(audio_genders)
    print(colored(f"Género musical seleccionado: {audios_selected.name}", "green"))
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
            print(colored(f"Añadida: {song_path.name}", "blue"))
    
    # Merge songs
    song = songs_list[0]
    for i in range(1,len(songs_list)):
        print(colored(f"Uniendo: {i}/{len(songs_list)-1}", "blue"))
        song += songs_list[i]

    print(colored("Guardando archivo de audio...", "blue"))
    song.export(output_song_path, format="wav")


def alphanumeric_characters(string):
    return re.sub(r'\W+', '', string)


def assets_creator(news_obj,
                   videos_default_assets_folder,
                   videos_temp_assets_folder,
                   videos_output_folder,
                   video_width,
                   video_height,
                   video_fps):
    #
    content_list = news_obj.data_arranged.split("\n\n")

    video_name = alphanumeric_characters(news_obj.link)

    assets_video_folder = Path(os.path.join(videos_temp_assets_folder, video_name))
    assets_video_folder.mkdir(exist_ok=True)

    images_folder = Path(os.path.join(assets_video_folder, "images_downloaded"))
    images_folder.mkdir(exist_ok=True)

    images_processed_folder = Path(os.path.join(assets_video_folder, "images_processed"))
    images_processed_folder.mkdir(exist_ok=True)

    images_processed_text_folder = Path(os.path.join(assets_video_folder, "images_processed_text"))
    images_processed_text_folder.mkdir(exist_ok=True)

    text_folder = Path(os.path.join(assets_video_folder, "text_content"))
    text_folder.mkdir(exist_ok=True)

    audio_folder = Path(os.path.join(assets_video_folder, "audio_files"))
    audio_folder.mkdir(exist_ok=True)

    song_folder = Path(os.path.join(assets_video_folder, "audio_song"))
    song_folder.mkdir(exist_ok=True)

    specs_dict = dict()
    specs_file_path = os.path.join(assets_video_folder, "specs.json5")
    video_file_path = os.path.join(videos_output_folder, video_name + ".mp4")

    video_font_bodies_path = os.path.join(videos_default_assets_folder, "fonts", "AveriaSerif-Bold.ttf")
    for e in content_list:
        if bool(re.search(r"[американскиегоḥā]", e)):
            video_font_bodies_path = os.path.join(videos_default_assets_folder, "fonts", "timesbd.ttf")
            break

    video_font_titles_path = os.path.join(videos_default_assets_folder, "fonts", "LTAsus-Heavy.ttf")
    description_file_path = os.path.join(videos_output_folder, video_name + "_description.txt")
    
    default_audios_folder = os.path.join(videos_default_assets_folder, "audio")
    song_path = os.path.join(song_folder, "song.wav")
    audio_track_generator(default_audios_folder, song_path)

    specs_dict["outPath"] = video_file_path
    specs_dict["width"] = video_width
    specs_dict["height"] = video_height
    specs_dict["fps"] = video_fps
    specs_dict["defaults"] = {"layer": {"fontPath": video_font_bodies_path}}

    c = 0
    current_background = ""
    current_background_caption = ""
    allowed_voices_list = allowed_voices("[Título] " + news_obj.title + "\n\n" + news_obj.data_arranged)
    article_voice = random.choice(allowed_voices_list)
    current_image_path = ""

    ''' TITLE '''
    text_name = str(c) + "_title"
    title_path = os.path.join(text_folder, text_name + ".txt")
    with open(title_path, "w", encoding="utf8") as f:
        # f.write(content_body)
        f.write(news_obj.title)
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
        print(colored("Generating:", "green"), text_name + ".wav")
    except subprocess.CalledProcessError as ex:
        print(colored("Error generating audio", "red"))
        logging.log(logging.ERROR, "Error generating audio file:", ex)

    # For json5 file
    specs_dict["clips"] = [
        {
            "duration": get_wave_duration(wave_path) + 2,
            "layers": [
                {
                    "type": "title-background",
                    "text": news_obj.title,
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
        f.write(news_obj.title + "\n") # @@@@

    ''' AUTHOR '''
    author_path = os.path.join(text_folder, str(c) + "_author.txt")
    with open(author_path, "w", encoding="utf8") as f:
        f.write(news_obj.author)

    # For json5 file
    specs_dict["clips"][0]["layers"].append(
        {
            "type": "slide-in-text",
            "text": news_obj.author,
            "position": "top-left",
            "fontSize": "0.02"
        }
    )

    ''' DATE '''
    date_string = str(news_obj.year) + "-" + str(news_obj.month) + "-" + str(news_obj.day)
    date_path = os.path.join(text_folder, str(c) + "_date.txt")
    with open(date_path, "w", encoding="utf8") as f:
        f.write(date_string)
    
    # For json5 file
    specs_dict["clips"][0]["layers"].append(
        {
            "type": "slide-in-text",
            "text": date_string,
            "position": "bottom-right",
            "fontSize": "0.02"
        }
    )

    ''' CONTENT '''
    for e in content_list:
        c += 1
        content_tag = e.split(" ")[0]
        content_body = " ".join(e.split(" ")[1:])
        if content_body == "":
            continue

        ''' BODIES '''
        if content_tag == "[Cuerpo]": # Files for text bodies
            text_name = str(c) + "_body"
            text_path = os.path.join(text_folder, text_name + ".txt")
            with open(text_path, "w", encoding="utf8") as f:
                f.write(content_body)
            print(colored(f"Generating audio for {text_name}", "yellow"))
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
                print(colored("Generating:", "green"), text_name + ".wav")
            except subprocess.CalledProcessError as ex:
                print(colored("Error generating audio file", "red"))
                logging.log(logging.ERROR, "Error generating audio file:", ex)
            
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
        
        ''' SUBTITLES '''
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

        ''' CAPTIONS '''
        if content_tag == "[Epígrafe]": # Files for captions
            caption_path = os.path.join(text_folder, str(c) + "_caption.txt")
            with open(caption_path, "w", encoding="utf8") as f:
                f.write(content_body)
            images_processed_text_path = os.path.join(images_processed_text_folder, Path(current_image_path).name)    
            put_caption_on_image_processed(current_image_path, images_processed_text_path, content_body, video_font_bodies_path)

        ''' IMAGES '''
        if content_tag == "[Imagen]":
            print(colored(f"Descargando: {content_body}", "yellow"))
            if not(content_body.startswith("http")):
                content_body = "https://www" + content_body.split("www")[1]
            image_ext = content_body.split(".")[-1]
            # image_ext = "jpg"
            image_name = str(c) + "_image." + image_ext
            image_processed_name = str(c) + "_image.jpg"
            image_path = os.path.join(images_folder, image_name)
            try:
                # Images downloader
                subprocess.run(["wget",
                                "-c", "-O",
                                image_path, content_body.split("://")[0] + "://" + urlp.quote(content_body.split("://")[1]),
                                "--no-check-certificate"], check=True)
                print(colored("Guardado", "green"), image_name)
                # Images processing
                image_processed_path = os.path.join(images_processed_folder, image_processed_name)
                current_image_path = image_processed_path
                image_for_video_generator(image_path, image_processed_path, video_width, video_height)
                image_processed_text_path = os.path.join(images_processed_text_folder, image_processed_name)
                image_for_video_generator(image_path, image_processed_text_path, video_width, video_height)
            except subprocess.CalledProcessError as ex:
                print(colored("Error downloading.", "red"))
                logging.log(logging.ERROR, "Error downloading:", ex)
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


def video_creator(news_obj,
                  videos_default_assets_folder,
                  videos_temp_assets_folder,
                  videos_output_folder,
                  video_width,
                  video_height,
                  video_fps):
    # Assets generation                  
    assets_creator(news_obj,
                   videos_default_assets_folder,
                   videos_temp_assets_folder,
                   videos_output_folder,
                   video_width,
                   video_height,
                   video_fps)
    # Video generation
    video_name = alphanumeric_characters(news_obj.link)
    assets_folder = os.path.join(videos_temp_assets_folder, video_name)
    specs_path = os.path.join(assets_folder, "specs.json5")
    try:
        subprocess.run(["editly", # Command line video editor Editly
                        specs_path
                        ], shell=True)
        print(colored("Generating video for:", "green"), news_obj.link)
    except subprocess.CalledProcessError as ex:
        print(colored("Error generating video file", "red"))
        logging.log(logging.ERROR, "Error generating video file:", ex)
        fail = True
        return fail

    # Assets cleaning
    shutil.rmtree(assets_folder) # Assets cleaning
    # source_video_path = os.path.join(article_scraped_path, article_id + ".mp4")
    # source_description_path = os.path.join(article_scraped_path, article_id + "_description.txt")
    # shutil.move(source_video_path, videos_to_upload_path)
    # shutil.move(source_description_path, videos_to_upload_path)


def videos_creator(func,
                   videos_default_assets_folder,
                   videos_temp_assets_folder,
                   videos_output_folder,
                   video_width,
                   video_height,
                   video_fps):
    # Create folders if they don't exist
    videos_temp_assets = Path(videos_temp_assets_folder)
    videos_temp_assets.mkdir(parents=True, exist_ok=True)
    videos_output = Path(videos_output_folder)
    videos_output.mkdir(parents=True, exist_ok=True)

    news_list = func() # Specific query result
    
    for news in news_list: # For each news
        video_creator(news,
                      videos_default_assets_folder,
                      videos_temp_assets_folder,
                      videos_output_folder,
                      video_width,
                      video_height,
                      video_fps)



''' Execution '''

def execution():
    videos_default_assets_folder = "videos_default_assets"
    videos_temp_assets_folder = "videos_temp_assets"
    videos_output_folder = "videos_to_upload"
    video_width = 1920
    video_height = 1080
    video_fps = 60

    videos_creator(db.get_link, # Query
                videos_default_assets_folder,
                videos_temp_assets_folder,
                videos_output_folder,
                video_width,
                video_height,
                video_fps)