from pathlib import Path
import os
import pickle



def load_all_words(news_content_path):
    tags_set = set()
    tags_dict = dict()
    p = Path(news_content_path)
    content_list  = list()

    c = 0
    for folder in p.iterdir():
        c += 1
        print(f"Article: {c}")
        file_name = os.path.join(folder, folder.name + ".txt")
        with open(file_name, "r", encoding="utf8") as f:
            content_list = f.read().split("\n\n")
        
        for e in content_list:
            if e.split(" ")[0] == "[Etiquetas]":
                tags = " ".join(e.split(" ")[1:]).lower().split(", ")
                if tags != [""]:
                    for t in tags:
                        tags_set.add(t)
                        if tags_dict.get(t) is not None:
                            tags_dict[t] += 1
                        else:
                            tags_dict[t] = 1

    aux_dict = dict(sorted(tags_dict.items(), key=lambda item:item[1], reverse=True))
    c = 0
    index_tag_dict = dict()
    for k in aux_dict.keys():
        index_tag_dict[c] = k
        c += 1

    tag_index_dict = dict()
    for k, v in index_tag_dict.items():
        tag_index_dict[v] = k
        
    with open("tags_set.pickle", "wb") as handle:
        pickle.dump(tags_set, handle, protocol=pickle.HIGHEST_PROTOCOL)

    with open("tags_dict.pickle", "wb") as handle:
        pickle.dump(tags_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)

    with open("index_tag_dict.pickle", "wb") as handle:
        pickle.dump(index_tag_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)

    with open("tag_index_dict.pickle", "wb") as handle:
        pickle.dump(tag_index_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)



news_content_path = "bbc_news_content_scraped"

load_all_words(news_content_path)

with open("tags_set.pickle", "rb") as handle:
    tags_set = pickle.load(handle)

with open("tags_dict.pickle", "rb") as handle:
    tags_dict = pickle.load(handle)

with open("index_tag_dict.pickle", "rb") as handle:
    index_tag_dict = pickle.load(handle)

with open("tag_index_dict.pickle", "rb") as handle:
    tag_index_dict = pickle.load(handle)

with open("keywords.txt", "w", encoding="utf8") as f:
    for k, v in index_tag_dict.items():
        # print(k, v, tags_dict[v])
        f.write(f"{k}:, {v} - {tags_dict[v]}")