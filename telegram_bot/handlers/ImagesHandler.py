from time import sleep

from telegram import InputMediaPhoto

from telegram_bot.keyboards.commandMarkup import get_command_markup
from telegram_bot.handlers import Handler


class ImagesHandler(Handler):
    def func(self, context, update):
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
                responses = context.bot.send_media_group(chat_id=update.effective_chat.id,
                                                         media=[InputMediaPhoto(open(str(image), "rb")) for image in
                                                                images])
                context.bot_data['ids'] = [response['photo'][-1]['file_id'] for response in responses]

            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="Updated on: {}".format(
                                         context.bot_data["last_update"].strftime("%d %b %Y")),
                                     reply_markup=get_command_markup())
            self.logger.info("IMAGES SENT")
            context.chat_data["last_update"] = context.bot_data["last_update"]
        else:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="You have the latest plot of {}".format(
                                         context.bot_data["last_update"].strftime("%d %b %Y")),
                                     reply_markup=get_command_markup())
            self.logger.info("IMAGES ALREADY SENT")
