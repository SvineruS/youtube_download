import json
from urllib import parse
import requests


def main():
    watch_url = input("url: ")
    id_ = get_id_from_watch_url(watch_url).strip()
    download_urls = get_download_urls_by_id(id_)

    while True:
        print("Choose quality:")
        print(*(f"#{i}: {q}" for i, q in enumerate(download_urls)), sep='\n')

        try:
            url = list(download_urls.values())[int(input("#"))]
        except (TypeError, KeyError):
            continue
        else:
            print("take it: ", url)
            break


def get_id_from_watch_url(url):
    d = parse.parse_qs(parse.urlsplit(url).query)
    for i in ('v',):  # todo more url formats
        if i in d:
            return d[i][0]
    raise Exception('Wrong url')


def get_download_urls_by_id(id_):
    resp = requests.get(f"https://www.youtube.com/get_video_info?video_id={id_}")
    video_info = parse.unquote(resp.text)
    player_response_string = video_info.split("player_response=")[1].split("&")[0]
    player_response_json = json.loads(player_response_string)
    if player_response_json['playabilityStatus']['status'] == 'UNPLAYABLE':
        raise Exception(player_response_json['playabilityStatus']['reason'])

    streaming_data = player_response_json['streamingData']
    # look at streaming_data['adaptiveFormats']. it contains more formats, for example mp3

    formats = streaming_data['formats']
    formats_sorted_by_quality = sorted(formats, key=lambda i: i['width'] * i['height'], reverse=True)
    formats_dict_by_quality = {f"{i['width']}x{i['height']}": i['url'] for i in formats_sorted_by_quality}
    return formats_dict_by_quality


if __name__ == "__main__":
    main()
