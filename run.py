from requests import get
from bs4 import BeautifulSoup

from datetime import datetime
from locale import setlocale, LC_ALL

from os import getenv
from os.path import dirname, realpath
from dotenv import load_dotenv
import argparse
import logging
import toolbox


# Set basic vars
websiteURL = "https://zoo.105.net/"
audioBaseURL = 'http://ms-pod.mediaset.net/repliche//{year:04d}/{month:02d}/{day:02d}/{daytext:s}_{day:02d}{month:02d}{year:04d}_zoo.mp3'

logging.basicConfig(level=logging.DEBUG)
parser = argparse.ArgumentParser()

# Parse CLI arguments
parser.add_argument('--audio', help='Send audio file',
                    dest='doSendAudio', default=False, action='store_true')
parser.add_argument('--video', help='Send video file',
                    dest='doSendVideo', default=False, action='store_true')
arguments = parser.parse_args()

if(not (arguments['doSendAudio'] and arguments['doSendVideo'])):
    logging.info('You didn\'t specify any action, run run.py -h')
    exit(0)


load_dotenv(dotenv_path=dirname(realpath(__file__))+'/config.env')
setlocale(LC_ALL, "it_IT.UTF8")

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
day, month, year = episodeTitles[0].split(' ')[-1].split('-')
today = datetime.today()

if (day == str(today.day) and month == str(today.month) and year == str(today.year)):
    telegram = toolbox.Telegram(getenv('TELEGRAM_API_TOKEN'), getenv(
        'TELEGRAM_CHAT_ID'), getenv('TELEGRAM_API_URL'))
    audioURL = audioBaseURL.format(
        day=today.day, month=today.month, year=today.year, daytext=today.strftime("%a").lower())

    filename = "{daytext:s}_{day:02d}{month:02d}{year:04d}_zoo".format(
        day=today.day, month=today.month, year=today.year, daytext=today.strftime("%a").lower())

    if (arguments['doSendAudio']):
        toolbox.download(audioURL, filename+'.mp3')
        r = telegram.sendAudio(filename+'.mp3')
        logging.debug(r)

    if (arguments['doSendVideo']):
        toolbox.download(videos[0], filename+'.mp4')
        r = telegram.sendVideo(filename+'.mp4')
        logging.debug(r)
