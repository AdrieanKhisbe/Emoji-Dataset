from pathlib import Path
import requests
from bs4 import BeautifulSoup
from urllib.request import urlretrieve
import re
import json

EMOJI_IMAGES_FAMILIES = ["apple", "google", "facebook", "windows", "twitter", "emojione", "samsung"]


def clean_string(s):
    return re.sub(r"([^\s\w]|_)+", "", s).strip()


def main():
    page = requests.get("https://unicode.org/emoji/charts/full-emoji-list.html")
    soup = BeautifulSoup(page.content, "html.parser")
    print("Status Code: ", page.status_code)
    trs = soup.find_all("tr")

    print("Tag Count: ", len(trs))

    for family in EMOJI_IMAGES_FAMILIES:
        Path(f"dataset/images/{family}/").mkdir(parents=True, exist_ok=True)

    dataset = []

    for element in trs:
        try:
            tds = element.find_all("td")

            emoji_index = tds[0].text
            emoji_unicode_str = tds[1].text
            emoji_unicode = emoji_unicode_str.split(" ")

            if len(emoji_unicode[0]) == 7:
                emoji_name = clean_string(tds[-1].text)

                print(emoji_index, emoji_unicode_str, emoji_name)

                entry = {
                    "index": emoji_index,
                    "unicode": emoji_unicode,
                    "name": emoji_name
                }

                for index, family in enumerate(EMOJI_IMAGES_FAMILIES):

                    try:
                        data_uri = tds[3 + index].findChildren()[0]["src"]
                        filename, _ = urlretrieve(data_uri, filename=f"dataset/images/{family}/{emoji_name}.png")
                        entry[f"{family}_emoji"] =  {
                            "image_path": filename,
                            "data_uri": data_uri
                        }

                    except Exception:
                        pass
                        # TODO
                dataset.append(entry)

        except Exception:
            pass

    print(f"Saving {len(dataset)} emoji entries")
    with open("dataset/dataset.json", "w") as file:
        json.dump(dataset, file, indent=2)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
