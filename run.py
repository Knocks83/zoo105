from requests import get, head
from bs4 import BeautifulSoup

from datetime import datetime, timedelta
from locale import setlocale, LC_ALL

from os import getenv, remove
from os.path import dirname, realpath, exists
from dotenv import load_dotenv
from time import sleep
import argparse
import logging
import toolbox


# Set basic vars
websiteURL = "https://zoo.105.net/"
audioBaseURL = 'http://ms-pod.mediaset.net/repliche//{year:04d}/{month:d}/{day:02d}/{daytext:s}_{day:02d}{month:02d}{year:04d}_zoo.mp3'

logging.basicConfig(level=logging.INFO)
parser = argparse.ArgumentParser()

# Parse CLI arguments
parser.add_argument('-a', '--audio', help='Send audio file',
                    dest='doSendAudio', default=False, action='store_true')
parser.add_argument('-v', '--video', help='Send video file',
                    dest='doSendVideo', default=False, action='store_true')
parser.add_argument('-b', '--before', help='Check the day before instead of current day',
                    dest='before', default=False, action='store_true')
arguments = parser.parse_args()

if(not (arguments.doSendAudio or arguments.doSendVideo)):
    logging.info('You didn\'t specify any action, run run.py -h')
    exit(0)


load_dotenv(dotenv_path=dirname(realpath(__file__))+'/config.env')
setlocale(LC_ALL, "it_IT.UTF8")

today = datetime.today()
filename = "{daytext:s}_{day:02d}{month:02d}{year:04d}_zoo".format(
    day=today.day, month=today.month, year=today.year, daytext=today.strftime("%a").lower())

telegram = toolbox.Telegram(getenv('TELEGRAM_API_TOKEN'), getenv(
    'TELEGRAM_CHAT_ID'), getenv('TELEGRAM_API_URL'))

if (arguments.before):
    today = today - timedelta(days=1)

if (arguments.doSendAudio):
    audioURL = audioBaseURL.format(
        day=today.day, month=today.month, year=today.year, daytext=today.strftime("%a").lower())

    tried = 0
    while not head(audioURL).status_code in [200, 302]:
        tried += 1
        if tried >= 10:
            exit(1)
        sleep(60)

    toolbox.download(audioURL, filename+'.mp3')
    r = telegram.sendAudio(filename+'.mp3')
    logging.debug(r)

    if exists(filename+'.mp3'):
        remove(filename+'.mp3')
    else:
        logging.error('Audio not found!')

if (arguments.doSendVideo):
    tried = 0
    while True:
        # Get and objectify the page
        page = get(websiteURL)
        soup = BeautifulSoup(page.content, "html.parser")

        videos = []
        episodeTitles = []

        # Find the div that contains the videos
        videoBox = soup.find(class_="cont_visualizzazione")

        # Loop through the divs with class box
        for episode in videoBox.findAll(class_="box"):
            # Find the webpage of the video and the title
            episodeURL = episode.find("a")['href']
            episodeTitles.append(episode.find("a").decode_contents())

            # Find the media url from inside the video webpage
            guid = toolbox.findGUID(episodeURL)
            videoURL = toolbox.findDownloadURL(guid)
            videos.append(videoURL)

        # split the date in different variables to check the date of the last media
        day, month = episodeTitles[0].split(' ')[-1].split('-')[:2]

        if (int(day) == today.day and int(month) == today.month):
            toolbox.download(videos[0], filename+'.mp4')
            r = telegram.sendVideo(filename+'.mp4', 'Lo Zoo di 105 - {day:02d}/{month:02d}/{year:04d}'.format(day=today.day, month=today.month, year=today.year))
            logging.debug(r)

            if exists(filename+'.mp4'):
                remove(filename+'.mp4')
            break
        else:
            tried += 1
            if tried >= 10:
                exit(1)
            sleep(60)
