# Zoo-105
This program was made to backup the episodes (both audio and video) of the radio program "Lo Zoo di 105" to a Telegram channel.

## Configuration
To configure the program, you just have to edit the `config.env` file and fill it with your values.
- TELEGRAM_API_TOKEN: The bot token you get with @BotFather on Telegram
- TELEGRAM_CHAT_ID: The ID of the chat where you want to send the media
- TELEGRAM_API_URL: That's the most complicate part: since the official Telegram API doesnt't support files as big as the ones we're sending, you need a custom API. I suggest the [TDLight Bot API](https://github.com/tdlight-team/tdlight-telegram-bot-api).

## Usage
To run the program you just have to run the file `run.py` with the adequate switch. The availabe switches are the following:
- `-v, --video` - Download the video of the current day
- `-a, --audio` - Download the audio of the current day
- `-b, --before` - Combined to any of the previous switches, it parses the day before instead of the current one

You have to use at least one switch between `--video` and `--audio`, otherwise the program will just exit.
