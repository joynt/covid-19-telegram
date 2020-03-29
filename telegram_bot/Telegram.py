import telegram
import urllib.request as request
from pathlib import Path

from telegram.ext import Updater, CommandHandler
import logging

import csv
import numpy as np
import matplotlib.pyplot as plt

from datetime import timedelta, datetime

from data import europe, countries, save_images
from data.run_italy import italy


class Telegram:
    def __init__(self, token: str):
        ## logging
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.INFO)
        self.token = token
        self.computed_new = False
        self.last_update = datetime.now() - timedelta(1)

        ## init
        self.image_path = Path('images/')
        self.image_path.mkdir(parents=True, exist_ok=True)

        ## bot
        self.updater = Updater(token=self.token, use_context=True)
        self.dispatcher = self.updater.dispatcher
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

    def _info(self, update, context):
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Simple bot that sends some plots about the COVID-19",
                                 reply_markup=self.reply_markup)

    def _start(self, update, context):
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="The avilable commands:",
                                 reply_markup=self.reply_markup)

    def _images(self, update, context):
        self.logger.info("Get request of images from [user: {}, name: {}, chat_id: {}]"
                         .format(update.effective_chat.username,
                                update.effective_chat.first_name,
                                update.effective_chat.id))
        if self.last_update < datetime.now() - timedelta(hours=6):
            self.logger.info("UPDATING IMAGES")
            countries(self.image_path)
            europe(self.image_path)
            # italy(self.image_path)
            self.last_update = datetime.now()
            self.id_image = {}

        for photo in self.image_path.glob('*.png'):
            if str(photo) in self.id_image:
                context.bot.send_photo(chat_id=update.effective_chat.id,
                                       photo=self.id_image[str(photo)])
            else:
                self.id_image[str(photo)] = context.bot.send_photo(chat_id=update.effective_chat.id,
                                                                   photo=open(str(photo), 'rb'))['photo'][-1]['file_id']
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Updated on: {}".format(self.last_update.strftime("%b-%d-%Y %H:%M")),
                                 reply_markup=self.reply_markup)
        self.logger.info("IMAGES SENT")
