import logging
import time

import inflect
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from helpers import check_auth, report_exception, write_pid
import outputter
from userinfo import E_MAIL, T_TOKEN


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


@check_auth
async def start(update, context):
    await context.bot.send_message(update.message.chat_id, "Hello Alice")


@check_auth
async def info(update, context):
    await context.bot.send_message(
        update.message.chat_id,
        """Provide a Reddit thread URL, batch size (optional), and 'old' for sorting comments by date (optional).
E.g.: https://www.reddit.com/r/nosleep/comments/3iex1h/im_a_search_and_rescue_officer_for_the_us_forest/ 500 old
""",
    )


@check_auth
async def scrape(update, context):
    beg = time.perf_counter()
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
    out_message = f"(Took {time.gmtime(time.perf_counter() - beg):%H:%M:%S}): " \
                  f"{url} -> {inflect.engine().plural('file', num_files)} -> {E_MAIL}"
    await context.bot.send_message(
        update.message.chat_id,
        out_message,
        disable_web_page_preview=True,
    )


@report_exception
def main():
    application = Application.builder().token(T_TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', info))
    application.add_handler(MessageHandler(filters=filters.TEXT, callback=scrape))
    application.run_polling()


if __name__ == '__main__':
    write_pid()
    main()
