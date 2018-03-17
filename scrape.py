import time
import json
import praw
import pprint
from pytz import utc, timezone
from datetime import datetime
from scrt import *


TRUE_EVENTS = '1uac3m'
FNAME_TXT = 'true_events{}{}.txt'
FNAME_JSON = 'true_events{}.json'
BYOLD = '_byold'
DATE = 'utctimestamp'
AUTHOR = 'authorname'
NONAME = 'noname'
UPS = 'ups'
TEXT = 'text'


def dump_submission(fname_json, submission_id, byold=''):
    with open(fname_json.format(byold), 'w', encoding='utf-8') as handler:
        json.dump(scrape(submission_id, byold), handler)


def scrape(submission_id, byold):
    thread = list()

    reddit = praw.Reddit(client_id=client_id,
                         client_secret=secret,
                         user_agent=agent)
    submission = reddit.submission(id=submission_id)

    if byold:
        submission.comment_sort = 'old'

    print("Replacing more...")
    submission.comments.replace_more(limit=None)
    print("...Replaced more")

    # first_comment = submission.comments.list()[0]
    # pprint.pprint(vars(first_comment))

    for comment in submission.comments.list():
        try:
            authorname = comment.author.name
        except AttributeError:
            authorname = NONAME
        thread.append({DATE: comment.created_utc,
                       AUTHOR: authorname,
                       UPS: comment.ups,
                       TEXT: comment.body})

    return thread


def json_to_text(fname_json, fname_txt, lim, byold=''):

    def write_in():
        nonlocal ind

        comment = next(thread)

        text = comment[TEXT]
        if text == '[deleted]':
            return

        handler.write(str(ind) + '\n')
        raw_date = datetime.utcfromtimestamp(comment[DATE])
        local_date = utc.localize(raw_date, is_dst=None).astimezone(timezone('Europe/Moscow'))
        handler.write(local_date.strftime("%d.%m.%Y %H:%M:%S") + '\n')
        handler.write(comment[AUTHOR] + '\n')
        handler.write("ups: " + str(comment[UPS]) + '\n\n')
        handler.write(text + '\n\n\n')

        ind += 1

    with open(fname_json.format(byold), encoding='utf-8') as data:
        thread = json.load(data)
    print("Thread is {} comment(s) long".format(len(thread)))
    thread = iter(thread)
    ind = 1
    iteration = 0
    while True:
        iteration += 1
        try:
            with open(fname_txt.format(byold, iteration), 'w', encoding='utf-8') as handler:
                while ind % lim:
                    write_in()
                write_in()
        except StopIteration:
            break


if __name__ == '__main__':
    start_time = time.time()
    dump_submission(FNAME_JSON, TRUE_EVENTS, BYOLD)
    elapsed_time = time.time() - start_time
    print()
    print()
    print(time.strftime("%H:%M:%S", time.gmtime(elapsed_time)))
    json_to_text(FNAME_JSON, FNAME_TXT, 500, BYOLD)
