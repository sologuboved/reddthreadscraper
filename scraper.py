import praw

from helpers import delete_pid, dump_utf_json, which_watch, write_pid
from userinfo import R_CLIENT_ID, R_CLIENT_SECRET, R_PASSWORD, R_USER_AGENT, R_USERNAME


class Batcher:
    def __init__(self, raw_thread, batch_size):
        self.raw_thread = raw_thread


class Scraper:
    def __init__(self, url, by_old, batch_size):
        self.url = url
        self.by_old = by_old
        self.batch_size = batch_size
        self.filename = self.get_filename()

    def get_filename(self):
        if self.url.endswith('/'):
            url = self.url[:-1]
        else:
            url = self.url
        return url.rsplit('/', 1)[-1]

    def get_thread(self):
        reddit = praw.Reddit(
            client_id=R_CLIENT_ID,
            client_secret=R_CLIENT_SECRET,
            password=R_PASSWORD,
            user_agent=R_USER_AGENT,
            username=R_USERNAME,
        )
        submission = reddit.submission(url=self.url)

        if self.by_old:
            submission.comment_sort = 'old'

        print("Replacing more...")
        submission.comments.replace_more(limit=None)
        print("...Replaced more")

        for comment in submission.comments.list():
            text = comment.body
            if text == '[deleted]':
                continue
            try:
                authorname = comment.author.name
            except AttributeError:
                authorname = 'NoName'
            yield {
                'utctimestamp': comment.created_utc,
                'author': authorname,
                'ups': comment.ups,
                'text': text,
            }


if __name__ == '__main__':
    pid_fname = write_pid()
    ('https://www.reddit.com/r/AskReddit/comments/ucaltb/what_are_some_simple_yet_incredibly/', False, False)
    delete_pid(pid_fname)
