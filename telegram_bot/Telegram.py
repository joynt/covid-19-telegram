import telegram
import urllib.request as request
from pathlib import Path

from telegram.ext import Updater, CommandHandler
import logging

import csv
import numpy as np
import matplotlib.pyplot as plt

from datetime import timedelta, datetime

from data import europe, countries
from data.run_italy import italy


class Telegram:

    def __init__(self, token: str):
        self.token = token
        self.id_image = {}
        self.compute_new = True
        self.last_update = datetime.now()

        ## init
        self.image_path = Path('images/')
        self.image_path.mkdir(parents=True, exist_ok=True)

        ## bot
        self.updater = Updater(token=self.token, use_context=True)
        self.dispatcher = self.updater.dispatcher
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.INFO)
        start_handler = CommandHandler('start', self._start)
        self.dispatcher.add_handler(start_handler)
        info_handler = CommandHandler('info', self._info)
        self.dispatcher.add_handler(info_handler)

    def start(self):
        self.updater.start_polling()
        self.updater.idle()

    def _start(self, update, context):
        custom_keyboard = [['/info']]
        reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="The avilable commands:",
                                 reply_markup=reply_markup)

    def _info(self, update, context):
        if self.last_update < datetime.now() - timedelta(hours=6) or self.compute_new:
            countries(self.image_path)
            # italy(self.image_path)
            self.last_update = datetime.now()
            self.compute_new = False

        for photo in self.image_path.glob('*.png'):
            if str(photo) in self.id_image:
                context.bot.send_photo(chat_id=update.effective_chat.id,
                                       photo=self.id_image[str(photo)],
                                       caption="Updated on: {}".format(self.last_update))
            else:
                self.id_image[str(photo)] = context.bot.send_photo(chat_id=update.effective_chat.id,
                                                                   photo=open(str(photo), 'rb'),
                                                                   caption="Updated on: {}".format(self.last_update))['photo'][-1]['file_id']
