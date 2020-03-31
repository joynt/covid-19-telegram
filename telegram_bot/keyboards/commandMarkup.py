from telegram import ReplyKeyboardMarkup


def get_command_markup() -> ReplyKeyboardMarkup:
    custom_keyboard = [['/images'], ['/info']]
    return ReplyKeyboardMarkup(custom_keyboard)
