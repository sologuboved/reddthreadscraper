import os

import scraper


async def output(url, by_old, batch_size, remove):
    filenames = await scraper.scrape(url=url, by_old=by_old, batch_size=batch_size, txt=True)
    # TODO: emailing
    num_filenames = len(filenames)
    if remove:
        print("Removing files...")
        for filename in filenames:
            try:
                os.remove(filename)
            except FileNotFoundError:
                pass
    return num_filenames


if __name__ == '__main__':
    print(output(
        url='https://www.reddit.com/r/Paranormal/comments/6l40lg/some_lesser_known_askreddit_paranormal_etc_threads/',
        by_old=True,
        batch_size=None,
        remove=False,
    ))
