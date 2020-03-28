from requests import get
import urllib.request as request
import telepot
from telepot.loop import MessageLoop
import time
import csv
import numpy as np
import matplotlib.pyplot as plt

from datetime import timedelta, datetime


class Telegram:

    def __init__(self, token: str):
        self.token = token
        self.id_image = {}
        self.compute_new = True

        italy_url = 'https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-andamento-nazionale/dpc-covid19-ita-andamento-nazionale.csv'
        confirmed_url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
        death_url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv'

        self.images = []
        self.all_url = {"Italy": italy_url, "confirmed": confirmed_url, "death": death_url}

        self.data = {}

        ## init
        self.getData()
        self.createFigures()

    def getData(self):

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

    def createFigures(self):
        plt.figure(figsize=(7, 7))
        plt.scatter(self.data["Hubey"]['days'], self.data["Hubey"]['data'], label='Hubei', s=20)
        x = np.array(self.data["Italy"]['days'][self.data["Italy"]['data'] > self.data["Hubey"]['days'][0]])
        y = self.data["Italy"]['data'][self.data["Italy"]['data'] > self.data["Hubey"]['days'][0]]
        plt.scatter(x, y, label='Italy', s=20)
        plt.legend()
        plt.xlabel('Days')
        plt.ylabel('Infected')
        plt.savefig('italy_hubei.png', dpi=300, bbox_inches='tight')
        self.images.append('italy_hubei.png')

    def run(self):
        bot = telepot.Bot(self.token)

        def handle(msg):
            content_type, chat_type, chat_id = telepot.glance(msg)
            if content_type == 'text':
                name = msg["from"]["first_name"]
                txt = msg['text']
                if '/info' in txt:
                    bot.sendMessage(chat_id, 'Hi, {}!'.format(name))
                    for photo in self.images:
                        bot.sendPhoto(chat_id=chat_id, photo=open(photo, 'rb'))


                elif '/set_expedition' in txt:
                    params = txt.split()[1:]

        MessageLoop(bot, handle).run_as_thread()
        print('listening')
        while (True):
            time.sleep(10)
