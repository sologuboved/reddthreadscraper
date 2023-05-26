import os

import scraper


def output(url, by_old, batch_size):
    filenames = scraper.scrape(url=url, by_old=by_old, batch_size=batch_size, txt=True)
    # TODO: emailing
    num_filenames = len(filenames)
    for filename in filenames:
        try:
            os.remove(filename)
        except FileNotFoundError:
            pass
    return num_filenames

