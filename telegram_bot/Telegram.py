import telegram
import urllib.request as request
from pathlib import Path

from telegram.ext import Updater, CommandHandler
import logging

import csv
import numpy as np
import matplotlib.pyplot as plt

from datetime import timedelta, datetime


class Telegram:

    def __init__(self, token: str):
        self.token = token
        self.id_image = {}
        self.compute_new = True
        self.last_update = datetime.now()

        italy_url = 'https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-andamento-nazionale/dpc-covid19-ita-andamento-nazionale.csv'
        confirmed_url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
        death_url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv'

        self.images = {}
        self.all_url = {"Italy": italy_url, "confirmed": confirmed_url, "death": death_url}

        self.data = {}

        ## init
        self.image_path = Path('images/')
        self.image_path.mkdir(parents=True, exist_ok=True)
        self._getData()
        self._createFigures()

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
        if self.last_update < datetime.now() - timedelta(hours=6):
            self._getData()
            self._createFigures()
            self.last_update = datetime.now()

        for photo in self.image_path.glob('*.png'):
            context.bot.send_photo(chat_id=update.effective_chat.id, photo=open(str(photo), 'rb'),
                                   caption="Updated on: {}".format(self.last_update))

    def _getData(self):
        self.last_update = datetime.now()
        ################## ITALY
        data_it = []
        csv_file = request.urlopen(self.all_url["Italy"]).read().decode('utf8').split("\n")
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            data_it.append(int(row['totale_casi']))

        days_it = np.arange(0, len(data_it), 1)

        self.data['Italy'] = {'data': np.array(data_it), 'days': days_it}

        ################## HUBEY

        data_hub = []
        csv_file = request.urlopen(self.all_url["confirmed"]).read().decode('utf8').split("\n")
        csv_reader = csv.DictReader(csv_file)

        for row in csv_reader:
            if row['Country/Region'] == 'China':
                if row['Province/State'] == 'Hubei':
                    data_hub = np.array(list(row.values())[4:-1]).astype('int')

        days_hub = np.arange(0, len(data_hub), 1)

        self.data['Hubey'] = {'data': data_hub, 'days': days_hub}

        ############### EUROPE

        clist = ['Italy', 'Spain', 'Germany', 'US', 'France', 'United Kingdom']
        tlist = []

        for country in clist:
            temp = []

            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                if row['Country/Region'] == country:
                    temp.append(np.array(list(row.values())[4:]).astype('int'))
            tlist.append(np.sum(temp, axis=0))

        dlist = []
        for country in clist:
            temp = []

            csv_file = request.urlopen(self.all_url["death"]).read().decode('utf8').split("\n")
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                if row['Country/Region'] == country:
                    temp.append(np.array(list(row.values())[4:]).astype('int'))
            dlist.append(np.sum(temp, axis=0))

        self.data['countries'] = {'tlist' : tlist, 'clist': clist, 'dlist': dlist}



    def _createFigures(self):
        plt.figure(figsize=(7, 7))
        plt.scatter(self.data["Hubey"]['days'], self.data["Hubey"]['data'], label='Hubei', s=20)
        x = np.array(self.data["Italy"]['days'][self.data["Italy"]['data'] > self.data["Hubey"]['days'][0]])
        y = self.data["Italy"]['data'][self.data["Italy"]['data'] > self.data["Hubey"]['days'][0]]
        plt.scatter(x, y, label='Italy', s=20)
        plt.legend()
        plt.xlabel('Days')
        plt.ylabel('Infected')
        plt.savefig(self.image_path / 'italy_hubei.png', dpi=300, bbox_inches='tight')


        ######### countries

        days = [np.arange(0, len(t), 1) for t in self.data['countries']['tlist']]
        days_t = [0, 8, 7, 10, 8, 13]
        ld_list = [46, 52, None, None, 53, 61]  # 46 is the index for 09/03, 52 for 15/03
        # 61 for 24/03

        colorlist = plt.cm.tab10(np.linspace(0, len(days_t) / 10, len(days_t)))
        fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(14, 7))

        for x, y, l, dt, ld, c in zip(days, self.data['countries']['tlist'], self.data['countries']['clist'], days_t, ld_list, colorlist):
            ax[0].plot(x - dt, y, label=l + ' (' + str(dt) + ' days delay)', color=c)
            ax[0].scatter(x - dt, y, color=c, s=30)
            if ld != None:
                ax[0].axvline(x=ld - dt, color=c)

        ax[0].set_xlabel('Days (country-wide lockdown at the vertical line)')
        ax[0].set_ylabel('Infected')
        ax[0].set_yscale('log')
        ax[0].set_xlim(10, 70)
        ax[0].set_ylim(1, 200000)
        ax[0].legend(loc=2)

        for x, y, l, dt, ld, c in zip(days, self.data['countries']['dlist'], self.data['countries']['clist'], days_t, ld_list, colorlist):
            ax[1].plot(x - dt, y, label=l + ' (' + str(dt) + ' days delay)', color=c)
            ax[1].scatter(x - dt, y, color=c, s=30)
            if ld != None:
                ax[1].axvline(x=ld - dt, color=c)

        ax[1].set_xlabel('Days (country-wide lockdown at the vertical line)')
        ax[1].set_ylabel('Deaths')
        ax[1].set_yscale('log')
        ax[1].set_xlim(10, 70)
        ax[1].set_ylim(0.9, 20000)
        ax[1].legend(loc=2)

        plt.savefig(self.image_path / 'countries.png', dpi=300, bbox_inches='tight')
