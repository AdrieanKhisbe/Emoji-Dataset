from pathlib import Path
import requests
from bs4 import BeautifulSoup
from urllib.request import urlretrieve
import re
import json


def clean_string(s):
    return re.sub(r'([^\s\w]|_)+', '', s).strip()


def main():

    page = requests.get(
        "https://unicode.org/emoji/charts/full-emoji-list.html")
    soup = BeautifulSoup(page.content, 'html.parser')
    print('Status Code: ', page.status_code)
    trs = soup.find_all('tr')

    print('Tag Count: ', len(trs))

    Path("dataset/images/apple/").mkdir(parents=True, exist_ok=True)
    Path("dataset/images/google/").mkdir(parents=True, exist_ok=True)
    Path("dataset/images/facebook/").mkdir(parents=True, exist_ok=True)
    Path("dataset/images/windows/").mkdir(parents=True, exist_ok=True)
    Path("dataset/images/twitter/").mkdir(parents=True, exist_ok=True)
    Path("dataset/images/emojione/").mkdir(parents=True, exist_ok=True)
    Path("dataset/images/samsung/").mkdir(parents=True, exist_ok=True)

    dataset = list()

    for element in trs:
        try:
            tds = element.find_all('td')

            emoji_index = tds[0].text
            emoji_unicode_str = tds[1].text
            emoji_unicode = emoji_unicode_str.split(' ')

            if len(emoji_unicode[0]) == 7:
                emoji_name = clean_string(tds[-1].text)

                print(emoji_index, emoji_unicode_str, emoji_name)

                entry = dict()
                entry['index'] = emoji_index
                entry['unicode'] = emoji_unicode
                entry['name'] = emoji_name

                try:
                    data_uri = tds[3].findChildren()[0]['src']
                    filename, m = urlretrieve(
                        data_uri, filename="dataset/images/apple/{}.png".format(emoji_name))
                    entry['apple_emoji'] = dict()
                    entry['apple_emoji']['image_path'] = filename
                    entry['apple_emoji']['data_uri'] = data_uri

                except Exception:
                    pass

                try:
                    data_uri = tds[4].findChildren()[0]['src']
                    filename, m = urlretrieve(
                        data_uri, filename="dataset/images/google/{}.png".format(emoji_name))
                    entry['google_emoji'] = dict()
                    entry['google_emoji']['image_path'] = filename
                    entry['google_emoji']['data_uri'] = data_uri
                except Exception:
                    pass

                try:
                    data_uri = tds[5].findChildren()[0]['src']
                    filename, m = urlretrieve(
                        data_uri, filename="dataset/images/facebook/{}.png".format(emoji_name))
                    entry['facebook_emoji'] = dict()
                    entry['facebook_emoji']['image_path'] = filename
                    entry['facebook_emoji']['data_uri'] = data_uri
                except Exception:
                    pass

                try:
                    data_uri = tds[6].findChildren()[0]['src']
                    filename, m = urlretrieve(
                        data_uri, filename="dataset/images/windows/{}.png".format(emoji_name))
                    entry['windows_emoji'] = dict()
                    entry['windows_emoji']['image_path'] = filename
                    entry['windows_emoji']['data_uri'] = data_uri
                except Exception:
                    pass

                try:
                    data_uri = tds[7].findChildren()[0]['src']
                    filename, m = urlretrieve(
                        data_uri, filename="dataset/images/twitter/{}.png".format(emoji_name))
                    entry['twitter_emoji'] = dict()
                    entry['twitter_emoji']['image_path'] = filename
                    entry['twitter_emoji']['data_uri'] = data_uri
                except Exception:
                    pass

                try:
                    data_uri = tds[8].findChildren()[0]['src']
                    filename, m = urlretrieve(
                        data_uri, filename="dataset/images/emojione/{}.png".format(emoji_name))
                    entry['emojione_emoji'] = dict()
                    entry['emojione_emoji']['image_path'] = filename
                    entry['emojione_emoji']['data_uri'] = data_uri
                except Exception:
                    pass

                try:
                    data_uri = tds[9].findChildren()[0]['src']
                    filename, m = urlretrieve(
                        data_uri, filename="dataset/images/samsung/{}.png".format(emoji_name))
                    entry['samsung_emoji'] = dict()
                    entry['samsung_emoji']['image_path'] = filename
                    entry['samsung_emoji']['data_uri'] = data_uri
                except Exception:
                    pass

                dataset.append(entry)

        except Exception:
            pass

    print(dataset)
    with open('dataset/dataset.json', 'w') as fp:
        json.dump(dataset, fp)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
