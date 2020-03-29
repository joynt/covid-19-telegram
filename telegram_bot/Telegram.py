import requests
import telegram
import urllib.request as request
from pathlib import Path

from telegram import InputMediaPhoto
from telegram.ext import Updater, CommandHandler
import logging

from datetime import timedelta, datetime

from data import europe, countries

COUNTRIES = ['Italy', 'Spain', 'Germany', 'US', 'France', 'United Kingdom']


class Telegram:
    def __init__(self, token: str):
        ## logging
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.INFO)
        self.token = token
        self.last_update = datetime(1970, 1, 1)
        self.id_image = {}

        ## init
        self.image_path = Path('images/')
        self.image_path.mkdir(parents=True, exist_ok=True)

        ## bot
        self.updater = Updater(token=self.token, use_context=True)
        self.job_queue = self.updater.job_queue
        self.dispatcher = self.updater.dispatcher

        ## job
        self.job_queue.run_repeating(self._update_job, interval=3600, first=0)

        ## handlers
        start_handler = CommandHandler('start', self._start)
        self.dispatcher.add_handler(start_handler)
        image_handler = CommandHandler('images', self._images)
        self.dispatcher.add_handler(image_handler)
        info_handler = CommandHandler('info', self._info)
        self.dispatcher.add_handler(info_handler)

        custom_keyboard = [['/images'], ['/info']]
        self.reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)

    def start(self):
        self.updater.start_polling()
        self.updater.idle()

    def _update_job(self, context: telegram.ext.CallbackContext):
        self.logger.info("Check updated data")
        data = requests.get("https://pomber.github.io/covid19/timeseries.json").json()
        last_update = data[list(data.keys())[0]][-1]['date']
        last_update = datetime.strptime(last_update, '%Y-%m-%d')
        if last_update > self.last_update:
            self.logger.info("START UPDATING IMAGES")
            countries(self.image_path, COUNTRIES)
            europe(self.image_path)
            # italy(self.image_path)
            self.last_update = last_update
            self.id_image = {}
            self.logger.info("END UPDATING IMAGES")

    def _info(self, update, context):
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Simple bot that makes some statistic about the COVID-19."
                                      "\nIf you want to contribute please visit: "
                                      "[Repo](https://github.com/joynt/covid-19-telegram)"
                                      "\nPlease be kind :)",
                                 parse_mode=telegram.ParseMode.MARKDOWN,
                                 reply_markup=self.reply_markup)

    def _start(self, update, context):
        self._info(update, context)

    def _images(self, update, context):
        self.logger.info("Get request of images from [user: {}, name: {}, chat_id: {}]"
                         .format(update.effective_chat.username,
                                 update.effective_chat.first_name,
                                 update.effective_chat.id))

        media = []
        names = []
        for photo in self.image_path.glob('*.png'):
            if str(photo) in self.id_image:
                media.append(InputMediaPhoto(self.id_image[str(photo)]))
            else:
                media.append(InputMediaPhoto(open(str(photo), 'rb')))
            names.append(str(photo))

        responses = context.bot.send_media_group(chat_id=update.effective_chat.id, media=media)

        if len(self.id_image) != len(names):
            self.id_image = {}
            for response, name in zip(responses, names):
                self.id_image[name] = response['photo'][-1]['file_id']

        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Updated on: {}".format(self.last_update.strftime("%d %b %Y")),
                                 reply_markup=self.reply_markup)
        self.logger.info("IMAGES SENT")
