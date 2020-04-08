import os

import numpy as np
import urllib.request as request
import csv
import matplotlib.pyplot as plt
from pathlib import Path


def europe(path: Path):
    url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'

    clist = ['Italy', 'Spain', 'Germany', 'US', 'France', 'United Kingdom']
    tlist = []

    csv_file = request.urlopen(url).read().decode('utf8').split("\n")

    for country in clist:
        temp = []
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            if row['Country/Region'] == country:
                temp.append(np.array(list(row.values())[4:]).astype('int'))
        tlist.append(np.sum(temp, axis=0))

    url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv'
    clist = ['Italy', 'Spain', 'Germany', 'US', 'France', 'United Kingdom']
    dlist = []

    csv_file = request.urlopen(url).read().decode('utf8').split("\n")

    for country in clist:
        temp = []
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            if row['Country/Region'] == country:
                temp.append(np.array(list(row.values())[4:]).astype('int'))
        dlist.append(np.sum(temp, axis=0))

    days = [np.arange(0, len(t), 1) for t in tlist]
    days_t = [0, 8, 7, 10, 8, 13]
    ld_list = [46, 52, None, None, 53, 61]  # 46 is the index for 09/03, 52 for 15/03
    # 61 for 24/03

    colorlist = plt.cm.tab10(np.linspace(0, len(days_t) / 10, len(days_t)))
    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(14, 7))

    for x, y, l, dt, ld, c in zip(days, tlist, clist, days_t, ld_list, colorlist):
        ax[0].plot(x - dt, y, label=l + ' (' + str(dt) + ' days delay)', color=c)
        ax[0].scatter(x - dt, y, color=c, s=30)
        if ld != None:
            ax[0].axvline(x=ld - dt, color=c)

    ax[0].set_xlabel('Days (country-wide lockdown at the vertical line)')
    ax[0].set_ylabel('Infected')
    ax[0].set_yscale('log')
    ax[0].set_ylim(1)
    ax[0].set_xlim(10)
    ax[0].legend(loc=2)

    for x, y, l, dt, ld, c in zip(days, dlist, clist, days_t, ld_list, colorlist):
        ax[1].plot(x - dt, y, label=l + ' (' + str(dt) + ' days delay)', color=c)
        ax[1].scatter(x - dt, y, color=c, s=30)
        if ld != None:
            ax[1].axvline(x=ld - dt, color=c)

    ax[1].set_xlabel('Days (country-wide lockdown at the vertical line)')
    ax[1].set_ylabel('Deaths')
    ax[1].set_yscale('log')
    ax[1].set_ylim(1)
    ax[1].set_xlim(10)
    ax[1].legend(loc=2)

    save = path / 'countries.png'
    if save.exists():
        os.remove(str(save))

    plt.savefig(save, dpi=400, bbox_inches='tight')
    plt.close(fig)