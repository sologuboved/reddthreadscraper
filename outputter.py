from email.message import EmailMessage
import os
import smtplib

import inflect

import scraper
from userinfo import E_MAIL_FROM, E_MAIL_TO, E_PASSWORD, E_SERVER


async def output(url, by_old, batch_size, remove):
    filenames = await scraper.scrape(url=url, by_old=by_old, batch_size=batch_size, txt=True)
    send_email(filenames)
    num_files = len(filenames)
    if remove:
        print("Removing files...")
        for filename in filenames:
            try:
                os.remove(filename)
            except FileNotFoundError:
                pass
        print('..done')
    else:
        print(f"Keeping {inflect.engine().plural('file', num_files)}")
    return num_files


def send_email(filenames):
    num_files = len(filenames)
    print(f"Sending {num_files} {inflect.engine().plural('file', num_files)}: {E_MAIL_FROM} -> {E_MAIL_TO}...")
    message = EmailMessage()
    message['Subject'] = f"[Reddthreadscraper] {filenames[0].split('.', 1)[0]}: {num_files}"
    message['From'] = E_MAIL_FROM
    message['To'] = E_MAIL_TO
    for filename in filenames:
        message.add_attachment(open(filename, 'r').read(), filename=filename)
    with smtplib.SMTP(E_SERVER, 587) as server:
        server.ehlo()
        server.starttls()
        server.login(E_MAIL_FROM, E_PASSWORD)
        server.sendmail(message['From'], message['To'], message.as_string())
    print('..done')


if __name__ == '__main__':
    import asyncio

    print(asyncio.run(output(
        url='https://www.reddit.com/r/Paranormal/comments/6l40lg/some_lesser_known_askreddit_paranormal_etc_threads/',
        by_old=True,
        batch_size=None,
        remove=False,
    )))
