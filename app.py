import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip

from queue import Queue  # Import Queue

TOKEN = "6945477074:AAHyfacl3SVW5AwDa7W5S3rbcnLm6oIQRX0"

# Define a function to add watermark to the video
def add_watermark(video_path, output_path, watermark_text):
    clip = VideoFileClip(video_path)
    txt_clip = TextClip(watermark_text, fontsize=70, color='white', bg_color='black')
    txt_clip = txt_clip.set_pos('center').set_duration(clip.duration)
    video_with_watermark = CompositeVideoClip([clip, txt_clip])
    video_with_watermark.write_videofile(output_path, codec='libx264', audio_codec='aac')
    return output_path

# Handler for /start command
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Hi! I am your video watermark bot. Send me a video, and I will add a watermark to it.')

# Handler for video messages
def handle_video(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    video_id = update.message.video.file_id
    video_path = f"{chat_id}.mp4"
    watermark_text = "Your Watermark Here"
    output_path = f"{chat_id}_watermarked.mp4"

    # Download the video
    video_file = context.bot.get_file(video_id)
    video_file.download(video_path)

    # Add watermark to the video
    add_watermark(video_path, output_path, watermark_text)

    # Send the watermarked video back to the user
    context.bot.send_video(chat_id, video=open(output_path, 'rb'))

    # Cleanup - delete temporary files
    os.remove(video_path)
    os.remove(output_path)

# Handler for unknown commands
def unknown(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Sorry, I didn't understand that command.")

def main() -> None:
    updater = Updater(TOKEN, use_context=True)  # Update: added use_context=True
    dp = updater.dispatcher

    # Register handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.video, handle_video))
    dp.add_handler(MessageHandler(Filters.command, unknown))

    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C
    updater.idle()

if __name__ == '__main__':
    main()
