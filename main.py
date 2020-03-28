# -*- coding: utf-8 -*-
"""
Created on Sat Jun  1 00:31:32 2019
@author: joynt
"""
import os

if os.name != 'nt':
    import daemon
    from daemon import pidfile

from secret import token
from telegram_bot import Telegram


if __name__ == "__main__":
    telegram = Telegram(token)

    if os.name == 'nt':
        telegram.start()
    else:
        pidfile = pidfile.TimeoutPIDLockFile('covidDaemon.pid')
        err = open('err.txt', 'w+')
        out = open('out.txt', 'w+')
        with daemon.DaemonContext(pidfile=pidfile, working_directory='./', stderr=err, stdout=out):
            telegram.start()
