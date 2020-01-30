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
    resp = requests.get(f"https://www.youtube.com/get_video_info?video_id={id_}").text
    resp = parse.unquote(resp)
    resp = resp.split("player_response=")[1].split("&")[0]
    resp = json.loads(resp)
    if resp['playabilityStatus']['status'] == 'UNPLAYABLE':
        raise Exception(resp['playabilityStatus']['reason'])

    resp = resp['streamingData']['formats']
    resp = sorted(resp, key=lambda i: i['width'] * i['height'], reverse=True)
    resp = {f"{i['width']}x{i['height']}": i['url'] for i in resp}
    return resp


if __name__ == "__main__":
    main()
