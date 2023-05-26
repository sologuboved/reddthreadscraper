from telegram.ext import Application, CommandHandler, MessageHandler, filters

from helpers import write_pid
from userinfo import T_TOKEN


async def scrape(update, context):
    message = update.message.text.split()
    url = message.pop(0)
    for item in message:
        try:
            batch_size = int(item)
        except ValueError:
            continue
        else:
            break
    else:
        batch_size = None
    if 'old' in message:
        by_old = True
    else:
        by_old = False
    await context.bot.send_message(
        update.message.chat_id,
        f"url: {url}, batch_size: {batch_size}, by_old: {by_old}",
        disable_web_page_preview=True,
    )


def main():
    application = Application.builder().token(T_TOKEN).build()
    application.add_handler(MessageHandler(filters=filters.TEXT, callback=scrape))
    application.run_polling()


if __name__ == '__main__':
    write_pid()
    main()
