from requests import get, post
from requests_toolbelt.multipart.encoder import MultipartEncoder
import xml.etree.ElementTree as ElementTree
from bs4 import BeautifulSoup
from json import loads


def findDownloadURL(guid: str) -> str:
    # Just a template, gotta replace [[GUID]] with the URL
    templateURL = "http://link.theplatform.eu/s/PR1GhC/media/guid/2702976343/[[GUID]]?mbr=true&formats=MPEG4&format=SMIL&assetTypes=HD,HBBTV,widevine,geoIT%7CgeoNo:HD,HBBTV,geoIT%7CgeoNo:HD,geoIT%7CgeoNo:SD,HBBTV,widevine,geoIT%7CgeoNo:SD,HBBTV,geoIT%7CgeoNo:SD,geoIT%7CgeoNo"

    get_response = get(templateURL.replace('[[GUID]]', guid))

    tree = ElementTree.fromstring(get_response.text)

    return tree[1][0][0][0][0].attrib['src']


def findGUID(episodeURL: str) -> str:
    page = get(episodeURL)
    soup = BeautifulSoup(page.content, "html.parser")

    script = soup.find('script')

    json = loads(script.decode_contents())
    embedURL = json['video']['embedUrl']

    guid = embedURL.split('=')[-1]

    return guid


def download(url, filename):
    # Stream the download to avoid saving it to memory
    with get(url, stream=True) as r:
        r.raise_for_status()
        with open(filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)


class Telegram:
    def __init__(self, token: str, chatID: str, botAPI='https://api.telegram.org/'):
        self.token = token
        self.chatID = chatID
        self.botAPI = botAPI

    def sendMessage(self, text: str):
        # Set post request parameters
        postParams = {
            'chat_id': self.chatID,
            'text': text
        }

        post(self.botAPI + "bot"+self.token +
             "/sendMessage", params=postParams)

    def sendAudio(self, filename: str) -> str:
        # Set post request parameters
        multipart = MultipartEncoder(
            fields={
                'chat_id': self.chatID,
                'audio': 'attach://' + filename,
                filename: (
                    filename,
                    open(filename, 'rb')
                )
            }
        )

        req = post(self.botAPI + "bot"+self.token + "/sendAudio",
                   data=multipart, headers={'Content-Type': multipart.content_type})
        return req.content.decode('utf-8')

    def sendVideo(self, filename: str, caption = '') -> str:
        # Set post request parameters
        multipart = MultipartEncoder(
            fields={
                'chat_id': self.chatID,
                'supports_streaming': 'true',
                'caption': caption,
                'video': 'attach://' + filename,
                filename: (
                    filename,
                    open(filename, 'rb')
                )
            }
        )

        req = post(self.botAPI + "bot"+self.token + "/sendVideo",
                   data=multipart, headers={'Content-Type': multipart.content_type})
        return req.content.decode('utf-8')
