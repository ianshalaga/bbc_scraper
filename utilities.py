import subprocess


def videos_to_upload_generator(news_videos_path, uploaded_videos_path):
    videos_to_upload_path = "videos_to_upload.txt"
    news_videos_list = list()
    uploaded_videos_list = list()
    videos_to_upload_list = list()
    with open(news_videos_path, "r", encoding="utf8") as f:
        news_videos_list = f.read().split("\n")
    with open(uploaded_videos_path, "r", encoding="utf8") as f:
        uploaded_videos_list = f.read().split("\n")
    
    for video in news_videos_list:
        if video not in uploaded_videos_list and video != "":
            videos_to_upload_list.append(video)
    
    with open(videos_to_upload_path, "w", encoding="utf8") as f:
        f.write("\n".join(videos_to_upload_list))


news_videos_path = "news_videos.txt"
uploaded_videos_path = "uploaded_videos.txt"
# videos_to_upload_generator(news_videos_path, uploaded_videos_path)

subprocess.run(["wget",
                "-c",
                "-O",
                "imagen.jpg",
                "https://ichef.bbci.co.uk/news/640/cpsprodpb/7B08/production/_89969413_simóncarrillocortesia.jpg",
                "--no-check-certificate"],
                check=True)