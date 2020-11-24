import json
from urllib import parse
import requests


def cli():
    watch_url = input("url: ")
    id_ = get_id_from_watch_url(watch_url).strip()
    download_urls = get_download_urls_by_id(id_)

    for i, q in enumerate(download_urls):
        print(f"#{i}", end=' ')
        if q['has_video']:
            print(f"[video {q['video']['width']}*{q['video']['height']}]", end=' ')
        if q['has_audio']:
            print("[audio]", end=' ')
        print(q['url'])


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
    video_details = player_response_json['videoDetails']

    formats = list(filter(None, map(
        get_item,
        streaming_data['formats'] + streaming_data['adaptiveFormats']
    )))
    thumbnails = [t['url'] for t in video_details['thumbnail']['thumbnails']]

    data = {
        'title':  video_details['title'],
        'length': video_details['lengthSeconds'],
        'description': video_details['shortDescription'],
        'formats': formats,
        'thumbnails': thumbnails
    }

    return data


def get_item(format):
    if 'url' not in format:
        return None

    has_video = 'width' in format
    has_audio = 'audioQuality' in format

    video, audio = {}, {}
    if has_video:
        video = {
            'width': format['width'],
            'height': format['height'],
        }
    if has_audio:
        audio = {
            'sample_rate': format['audioSampleRate'],
            'channels': format['audioChannels']
        }

    item = {
        'url': format['url'],
        'has_video': has_video,
        'video': video,
        'has_audio': has_audio,
        'audio': audio,
        'bitrate': format['bitrate'],
    }
    return item


if __name__ == "__main__":
    cli()
