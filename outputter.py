import os
import smtplib

import scraper
from userinfo import E_MAIL_FROM, E_MAIL_TO, E_PASSWORD, E_SERVER


async def output(url, by_old, batch_size, remove):
    filenames = await scraper.scrape(url=url, by_old=by_old, batch_size=batch_size, txt=True)
    send_email(filenames)
    num_filenames = len(filenames)
    if remove:
        print("Removing files...")
        for filename in filenames:
            try:
                os.remove(filename)
            except FileNotFoundError:
                pass
    return num_filenames


def send_email(filenames):
    print(f"Sending {len(filenames)} files from {E_MAIL_FROM} to {E_MAIL_TO}...")


if __name__ == '__main__':
    import asyncio

    # print(asyncio.run(output(
    #     url='https://www.reddit.com/r/Paranormal/comments/6l40lg/some_lesser_known_askreddit_paranormal_etc_threads/',
    #     by_old=True,
    #     batch_size=None,
    #     remove=False,
    # )))
    send_email(['true_events.txt'])
