import logging

from telegram.ext import CommandHandler


class Handler:
    def __init__(self, endpoint: str, handler):
        handler.add_handler(CommandHandler(endpoint, self.func))
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.INFO)

    def func(self, context, update):
        pass
