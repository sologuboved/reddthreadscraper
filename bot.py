import time

import inflect
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from helpers import write_pid
import outputter
from userinfo import E_MAIL, T_TOKEN


async def scrape(update, context):
    start = time.perf_counter()
    in_message = update.message.text.split()
    url = in_message.pop(0)
    for item in in_message:
        try:
            batch_size = int(item)
        except ValueError:
            continue
        else:
            break
    else:
        batch_size = None
    if 'old' in in_message:
        by_old = True
    else:
        by_old = False
    num_files = outputter.output(url, by_old, batch_size)
    out_message = f"(Took {time.gmtime(time.perf_counter() - start):%H:%M:%S}): " \
                  f"{url} -> {inflect.engine().plural('file', num_files)} -> {E_MAIL}"
    await context.bot.send_message(
        update.message.chat_id,
        out_message,
        disable_web_page_preview=True,
    )


def main():
    application = Application.builder().token(T_TOKEN).build()
    application.add_handler(MessageHandler(filters=filters.TEXT, callback=scrape))
    application.run_polling()


if __name__ == '__main__':
    write_pid()
    main()
