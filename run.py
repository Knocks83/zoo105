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
audioBaseURL = 'http://dr-pod.mediaset.net/repliche//{year:04d}/{month:d}/{day:d}/{daytext:s}_{day:02d}{month:02d}{year:04d}_zoo.mp3'
basePath = dirname(realpath(__file__)) + '/'

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

# Load the configuration from the dotenv file
load_dotenv(dotenv_path=dirname(realpath(__file__))+'/config.env')
# Since the day names (lunedì, martedì etc) are in italian, set the locale to italian
setlocale(LC_ALL, "it_IT.UTF8")

# Get the current day and generate the telegram object
today = datetime.today()
telegram = toolbox.Telegram(getenv('TELEGRAM_API_TOKEN'), getenv(
    'TELEGRAM_CHAT_ID'), getenv('TELEGRAM_API_URL'))

# If the script is configured to elaborate a day before, edit the today var
if (arguments.before):
    today = today - timedelta(days=1)

# After checking the day, calculate the filename of the episode
filename = basePath + "{daytext:s}_{day:02d}{month:02d}{year:04d}_zoo".format(
    day=today.day, month=today.month, year=today.year, daytext=today.strftime("%a").lower())

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

        # DUE TO THE FALSE POSITIVES, THIS CHECK HAS BEEN REPLACED BY THE ONE UNDER IT
        # Check if the title contains the day as digit OR at least the shortened weekday name (lun, mar, mer, gio, ven)
        #check = (str(today.day) in episodeTitles[0]) or (today.strftime("%a").lower() in episodeTitles[0].lower())
        # Check if the title contains the digits of the day
        check = (str(today.day) in episodeTitles[0])

        # Check if the title contains the month as digit OR at least the shortened month name (gen, feb, mar, apr, ...)
        check = check and ((str(today.month) in episodeTitles[0]) or (today.strftime("%b").lower() in episodeTitles[0].lower()))

        if (check):
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
