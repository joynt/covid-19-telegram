# -*- coding: utf-8 -*-
"""
Created on Sat Jun  1 00:31:32 2019
@author: joynt
"""
import os
from pathlib import Path

if os.name != 'nt':
    import daemon
    from daemon import pidfile

from secret import dev_token as token
from telegram_bot import Telegram
from datetime import datetime


if __name__ == "__main__":
    telegram = Telegram(token)

    if os.name == 'nt':
        telegram.start()
    else:
        log = Path("log/")
        log.mkdir(parents=True, exist_ok=True)
        pidfile = pidfile.TimeoutPIDLockFile(log / 'covidDaemon_{}.pid'.format(datetime.now().ctime()))
        err = open(log / 'err_{}.txt'.format(datetime.now().ctime()), 'w+')
        out = open(log / 'out_{}.txt'.format(datetime.now().ctime()), 'w+')
        with daemon.DaemonContext(pidfile=pidfile, working_directory='./', stderr=err, stdout=out):
            telegram.start()
