# Zoo-105
This program was made to backup the episodes (both audio and video) of the radio program "Lo Zoo di 105" to a Telegram channel.

It checks on their website if there's a video with the date corresponding to today's date. If the video exists, it downloads and uploads both the audio and the video to a defined chat on Telegram.

## Configuration
To configure the program, you just have to edit the `config.env` file and fill it with your values.
- TELEGRAM_API_TOKEN: The bot token you get with @BotFather on Telegram
- TELEGRAM_CHAT_ID: The ID of the chat where you want to send the media
- TELEGRAM_API_URL: That's the most complicate part: since the official Telegram API doesnt't support files as big as the ones we're sending, you need a custom API. I suggest the [TDLight Bot API](https://github.com/tdlight-team/tdlight-telegram-bot-api).
