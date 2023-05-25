import datetime

import praw
from pytz import timezone, utc

from userinfo import R_CLIENT_ID, R_CLIENT_SECRET, R_PASSWORD, R_USER_AGENT, R_USERNAME


def dump_submission(fname_json, submission_id, by_old=False):
    with open(fname_json.format(by_old), 'w', encoding='utf-8') as handler:
        json.dump(scrape_tread(submission_id, by_old), handler)


def scrape_tread(submission_id, by_old):
    thread = list()

    reddit = praw.Reddit(
        client_id=R_CLIENT_ID,
        client_secret=R_CLIENT_SECRET,
        password=R_PASSWORD,
        user_agent=R_USER_AGENT,
        username=R_USERNAME,
    )
    submission = reddit.submission(id=submission_id)

    if by_old:
        submission.comment_sort = 'old'

    print("Replacing more...")
    submission.comments.replace_more(limit=None)
    print("...Replaced more")

    for comment in submission.comments.list():
        try:
            authorname = comment.author.name
        except AttributeError:
            authorname = 'NoName'
        thread.append({
            'utctimestamp': comment.created_utc,
            'authorname': authorname,
            'ups': comment.ups,
            'text': comment.body,
        })

    return thread


def json_to_text(fname_json, fname_txt, lim, byold=''):
    def write_in():
        nonlocal ind

        comment = next(thread)

        text = comment[TEXT]
        if text == '[deleted]':
            return

        handler.write(str(ind) + '\n')
        raw_date = datetime.datetime.utcfromtimestamp(comment[DATE])
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
