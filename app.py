#!/usr/bin/python3
# Watermark Telegram Bot by uidops

import sys
import time
import os
import telepot
import telepot.loop
from colorama import (Fore, init)
from PIL import Image, ImageEnhance
from io import BytesIO
from tqdm import tqdm
from datetime import datetime

init()

print(Fore.GREEN + "Starting ...\n" + Fore.RESET)
api = "6663409312:AAHHe_KzigIf9GVMk6fsz4H6kUFJVOKxZxc"
bot = telepot.Bot(api)

# Dictionary to store processed image count for each day
stats = {}


class ImageProcessor():
    """Image processor class for watermark handling."""

    def __init__(self, file):
        """Initialization method."""
        self.file_name_origin = file
        self.logo_file = "logo.png"
        self.file_name = None  # Initialize file_name attribute

        self.logoIm = Image.open(self.logo_file).convert("RGBA")
        self.logo_width, self.logo_height = self.logoIm.size

        self.im = Image.open(self.file_name_origin)
        self.width, self.height = self.im.size

        self.progress = 0

    def add_watermark(self):
        """A method for adding a watermark to a picture."""
        total_pixels = self.width * self.height
        processed_pixels = 0

        for x in tqdm(range(self.width), desc="Processing image", unit="pixel"):
            for y in range(self.height):
                # Your image processing logic here
                processed_pixels += 1
                self.progress = processed_pixels / total_pixels

        # Move watermark to center
        center_x = (self.width - self.logo_width) // 2
        center_y = (self.height - self.logo_height) // 2
        seg = (center_x, center_y)

        # Add watermark with 50% opacity
        watermark = self.logoIm.copy()
        alpha = ImageEnhance.Brightness(watermark.split()[3]).enhance(0.5)
        watermark.putalpha(alpha)
        self.im.paste(watermark, seg, watermark)

        self.file_name = "{}_logo.{}".format(".".join(self.file_name_origin.split(".")[:-1]),
                                            self.file_name_origin.split(".")[-1])

        self.im.save(self.file_name)  # Save image to a file for sharing

    def get_output_name(self):
        """Returns the file name."""
        return self.file_name


def process_image(media_id, file_name):
    bot.download_file(file_id=media_id, dest=file_name)
    img = ImageProcessor(file_name)
    img.add_watermark()
    return img


def send_watermarked_image(chat_id, media_id, msg_id, caption=None):
    # To support sending the caption with the watermarked photo,
    # we download the original photo as bytes and send it as a photo.
    file_name = "./temp/{}.jpg".format(media_id)
    img = process_image(media_id, file_name)

    # Convert the watermarked image to bytes
    output = BytesIO()
    img.im.save(output, format='JPEG')
    output.seek(0)

    if caption:
        # Sending photo with caption
        bot.sendPhoto(chat_id=chat_id, photo=output, caption=caption,
                      reply_to_message_id=msg_id)
    else:
        # Sending photo without caption
        bot.sendPhoto(chat_id=chat_id, photo=output, reply_to_message_id=msg_id)

    # Update statistics
    date_str = datetime.today().strftime('%Y-%m-%d')
    stats[date_str] = stats.get(date_str, 0) + 1


def send_total_stats(chat_id):
    # Send statistics of processed images for each day
    total_stats = "\n".join([f"*{date}:* {count} 😊" for date, count in stats.items()])
    bot.sendMessage(chat_id=chat_id, text="*Total processed images:* \n" + total_stats, parse_mode="Markdown")


def send_welcome_message(chat_id):
    welcome_message = "Welcome to the Image Watermark Bot!\n\n" \
                      "Send me images, and I will add a watermark to them for you."
    bot.sendMessage(chat_id=chat_id, text=welcome_message)


def robot_handler(msg):
    """Telegram Bot handler function."""
    user_id = msg["chat"]["id"]
    msg_id = msg["message_id"]

    if "forward_from_chat" in msg and "photo" in msg:
        # Forwarded image from channel with caption
        media_id = msg["photo"][-1]["file_id"]
        caption = msg.get("caption", None)
        send_watermarked_image(user_id, media_id, msg_id, caption)
    elif "photo" in msg.keys():
        # Regular image from user
        media_id = msg["photo"][-1]["file_id"]
        send_watermarked_image(user_id, media_id, msg_id)
    elif "text" in msg and msg["text"].lower() == "/start":
        # User started the bot, send welcome message
        send_welcome_message(user_id)
    elif "text" in msg and msg["text"].lower() == "/total":
        # User requested total statistics
        send_total_stats(user_id)
    else:
        bot.sendMessage(chat_id=user_id, text="Unsupported message type", reply_to_message_id=msg_id)
        return 0


if __name__ == "__main__":
    if not os.path.isdir("temp"):
        os.mkdir("temp")

    try:
        me = bot.getMe()
    except telepot.exception.UnauthorizedError:
        print(Fore.RED + "UnauthorizedError" + Fore.RESET)
        sys.exit(1)

    for i in me.keys():
        print(Fore.MAGENTA + "\t{}: {}{}".format(i, Fore.LIGHTBLUE_EX, me[i]) + Fore.RESET)

    telepot.loop.MessageLoop(bot, robot_handler).run_as_thread()

    print(Fore.CYAN + "\nCtrl+C for shutdown..." + Fore.RESET)

    try:
        while 1:
            time.sleep(18000)
    except KeyboardInterrupt:
        sys.exit("\n")
