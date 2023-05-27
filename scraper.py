import asyncio
import datetime

import asyncpraw
from pytz import timezone, utc

from helpers import delete_pid, dump_utf_json, which_watch, write_pid
from userinfo import R_CLIENT_ID, R_CLIENT_SECRET, R_PASSWORD, R_USER_AGENT, R_USERNAME


def get_filename(url):
    if url.endswith('/'):
        url = url[:-1]
    else:
        url = url
    return url.rsplit('/', 1)[-1]


async def get_submission(reddit, url, by_old):
    submission = await reddit.submission(url=url, fetch=False)

    if by_old:
        submission.comment_sort = 'old'
    await submission.load()

    print("Replacing more...")
    await submission.comments.replace_more(limit=None)
    print("...Replaced more")

    return submission


def get_body_and_comments(permalink, post_text, post_author, post_utctimestamp, post_ups, raw_comments):
    yield {
        '#': 0,
        'permalink': permalink,
        'utctimestamp': post_utctimestamp,
        'author': post_author,
        'ups': post_ups,
        'text': post_text,
    }
    index = 0
    for comment in raw_comments:
        text = comment.body
        if text == '[deleted]':
            continue
        index += 1
        try:
            comment_author = comment.author.name
        except AttributeError:
            comment_author = '[NoName]'
        yield {
            '#': index,
            'permalink': comment.permalink,
            'utctimestamp': comment.created_utc,
            'author': comment_author,
            'ups': comment.ups,
            'text': text,
        }


def get_batch(raw_tread, batch_size):
    batch = list()
    count = index = 0
    for comment in raw_tread:
        batch.append(comment)
        count += 1
        if count == batch_size:
            yield index, batch
            batch = list()
            count = 0
            index += 1
    yield index, batch


def write_txt(thread, filename):
    filename += '.txt'
    count = 0
    with open(filename, 'w', encoding='utf-8') as handler:
        for comment in thread:
            count += 1
            handler.write(f"""{utc.localize(
                datetime.datetime.utcfromtimestamp(comment['utctimestamp']), 
                is_dst=None,
            ).astimezone(timezone('Europe/Moscow')).strftime("%d.%m.%Y %H:%M:%S")}
#{comment['#']}
{comment['author']}
{comment['ups']} ups
{comment['permalink']}

{comment['text']}
____

""")
    print(f"Dumping {count} entries into {filename}...")
    return filename


def write_json(thread, filename):
    filename += '.json'
    dump_utf_json(thread, filename)
    return filename


@which_watch
async def scrape(url, by_old, batch_size, txt):
    raw_filename = get_filename(url)
    print(f"({datetime.datetime.now():%Y-%m-%d %H:%M:%S}) Scraping {url}, destination {raw_filename}...\n")
    writer = [write_json, write_txt][txt]
    async with asyncpraw.Reddit(
        client_id=R_CLIENT_ID,
        client_secret=R_CLIENT_SECRET,
        password=R_PASSWORD,
        user_agent=R_USER_AGENT,
        username=R_USERNAME,
    ) as reddit:
        submission = await get_submission(reddit, url, by_old)
        num_comments = submission.num_comments
        try:
            post_author = submission.author.name
        except AttributeError:
            post_author = '[NoName]'
        raw_comments = submission.comments.list()
        raw_thread = get_body_and_comments(
            submission.permalink,
            f"{submission.title}\n\n{submission.selftext}",
            post_author,
            submission.created_utc,
            submission.score,
            raw_comments,
        )
    if batch_size:
        filenames = list()
        if num_comments > batch_size + 9:
            zfill = len(str(num_comments // batch_size + 1))
            for index, batch in get_batch(raw_thread, batch_size):
                filename = writer(batch, f'{raw_filename}_{str(index).zfill(zfill)}')
                filenames.append(filename)
            print(f"{len(filenames)} ready")
            return filenames
    return [writer(list(raw_thread), raw_filename)]


if __name__ == '__main__':
    pid_fname = write_pid()
    # print(scrape(
    #     'https://www.reddit.com/r/AskReddit/comments/ucaltb/what_are_some_simple_yet_incredibly/',
    #     False,
    #     1000,
    #     True,
    # ))
    print(asyncio.run(scrape(
        url='https://www.reddit.com/r/Paranormal/comments/6l40lg/some_lesser_known_askreddit_paranormal_etc_threads/',
        by_old=True,
        batch_size=None,
        txt=True,
    )))
    delete_pid(pid_fname)
