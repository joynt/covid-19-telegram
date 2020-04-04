import os
import sys
from threading import Thread
from time import sleep

import requests
import telegram
import urllib.request as request
from pathlib import Path

from telegram import InputMediaPhoto
from telegram.ext import Updater, CommandHandler, PicklePersistence, Filters
import logging

from datetime import timedelta, datetime

from data import europe, countries, world
from secret import dev
from .keyboards import get_command_markup

COUNTRIES = ['Italy', 'Spain', 'Germany', 'US', 'France', 'United Kingdom']


class Telegram:
    def __init__(self, token: str):
        ## logging
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.INFO)
        self.token = token

        ## init
        self.image_path = Path('images/')
        self.image_path.mkdir(parents=True, exist_ok=True)

        ## persistence
        persistence = PicklePersistence(filename="{}.pkl".format(__name__))

        ## bot
        self.updater = Updater(token=self.token, persistence=persistence, use_context=True)
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

        ## dev handlers
        restart_handler = CommandHandler('restart', self._restart, filters=Filters.user(username='@{}'.format(dev)))
        self.dispatcher.add_handler(restart_handler)

    def start(self):
        self.updater.start_polling()
        self.updater.idle()

    def _update_job(self, context: telegram.ext.CallbackContext):
        self.logger.info("Check updated data")
        data = requests.get("https://pomber.github.io/covid19/timeseries.json").json()
        last_update_str = data[list(data.keys())[0]][-1]['date']
        last_update = datetime.strptime(last_update_str, '%Y-%m-%d')
        try:
            update = last_update > context.bot_data["last_update"]
        except KeyError:
            update = True
        if update:
            path = self.image_path / last_update_str
            path.mkdir(parents=True, exist_ok=True)
            context.bot_data["updating"] = True
            self.logger.info("START UPDATING IMAGES")
            countries(path, COUNTRIES)
            europe(path)
            world(path)
            temp = {"last_update": last_update,
                    "media": [p for p in path.glob('*.png')],
                    "updating": False}
            context.bot_data.update(temp)
            self.logger.info("END UPDATING IMAGES")

    def _info(self, update, context):
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Simple bot that makes some statistic about the COVID-19."
                                      "\nIf you want to contribute please visit: "
                                      "[Repo](https://github.com/joynt/covid-19-telegram)"
                                      "\nPlease be kind :)",
                                 parse_mode=telegram.ParseMode.MARKDOWN,
                                 reply_markup=get_command_markup())

    def _start(self, update, context):
        self._info(update, context)

    def _images(self, update, context):
        self.logger.info("Get request of images from [user: {}, name: {}, chat_id: {}]"
                         .format(update.effective_chat.username,
                                 update.effective_chat.first_name,
                                 update.effective_chat.id))

        # Check of the last update sent to the user
        try:
            already_sent = context.chat_data["last_update"] == context.bot_data["last_update"]
        except KeyError:
            already_sent = False

        if not already_sent:
            # Check updating flag
            if context.bot_data["updating"]:
                context.bot.send_message(chat_id=update.effective_chat.id,
                                         text="I'm updating, I'll reply you when I'm ready",
                                         reply_markup=get_command_markup())
            # Wait if updating
            while context.bot_data["updating"]:
                sleep(5)

            # if ids is present then send the ids
            try:
                images = context.bot_data["ids"]
                context.bot.send_media_group(chat_id=update.effective_chat.id,
                                             media=[InputMediaPhoto(image) for image in images])
            # open file otherwise
            except KeyError:
                images = context.bot_data["media"]
                files = [open(str(image), "rb") for image in images]
                responses = context.bot.send_media_group(chat_id=update.effective_chat.id,
                                                         media=[InputMediaPhoto(file) for file in files])
                [file.close() for file in files]
                context.bot_data['ids'] = [response['photo'][-1]['file_id'] for response in responses]

            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="Updated on: {}".format(context.bot_data["last_update"].strftime("%d %b %Y")),
                                     reply_markup=get_command_markup())
            self.logger.info("IMAGES SENT")
            context.chat_data["last_update"] = context.bot_data["last_update"]
        else:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="You have the latest plot of {}".format(context.bot_data["last_update"].strftime("%d %b %Y")),
                                     reply_markup=get_command_markup())
            self.logger.info("IMAGES ALREADY SENT")

    def __stop_and_restart(self):
        """Gracefully stop the Updater and replace the current process with a new one"""
        self.updater.stop()
        os.execl(sys.executable, sys.executable, *sys.argv)

    def _restart(self, update, context):
        update.message.reply_text('Bot is restarting...')
        Thread(target=self.__stop_and_restart).start()
