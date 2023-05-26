import datetime

import praw

from helpers import delete_pid, dump_utf_json, get_abs_path, which_watch, write_pid
from userinfo import R_CLIENT_ID, R_CLIENT_SECRET, R_PASSWORD, R_USER_AGENT, R_USERNAME


class Scraper:
    def __init__(self, url, by_old, batch_size, txt):
        self.url = url
        self.by_old = by_old
        self.batch_size = batch_size
        if txt:
            self.writer = self.write_txt
        else:
            self.writer = self.write_json
        self.filename = get_abs_path(self.get_filename())

    def get_filename(self):
        if self.url.endswith('/'):
            url = self.url[:-1]
        else:
            url = self.url
        return url.rsplit('/', 1)[-1]

    def get_submission(self):
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

        return submission

    @staticmethod
    def get_comments(submission):
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

    def get_batch(self, raw_tread):
        batch = list()
        count = index = 0
        for comment in raw_tread:
            batch.append(comment)
            count += 1
            if count == self.batch_size:
                yield index, batch
                batch = list()
                count = 0
                index += 1
        yield index, batch

    @staticmethod
    def write_txt(thread, filename):
        filename += '.txt'

        return filename

    @staticmethod
    def write_json(thread, filename):
        filename += '.json'
        dump_utf_json(thread, filename)
        return filename

    @which_watch
    def main(self):
        print(f"({datetime.datetime.now():%Y-%m-%d %H:%M:%S}) Scraping {self.url}, destination {self.filename}...\n")
        submission = self.get_submission()
        num_comments = submission.num_comments
        raw_thread = self.get_comments(submission)
        if self.batch_size:
            filenames = list()
            if num_comments > self.batch_size + 9:
                zfill = len(str(num_comments // self.batch_size + 1))
                for index, batch in self.get_batch(raw_thread):
                    filename = self.writer(batch, f'{self.filename}_{str(index).zfill(zfill)}')
                    filenames.append(filename)
                return filenames
        return self.writer(list(raw_thread), self.filename)


if __name__ == '__main__':
    pid_fname = write_pid()
    print(Scraper(
        'https://www.reddit.com/r/AskReddit/comments/ucaltb/what_are_some_simple_yet_incredibly/',
        False,
        1000,
        False,
    ).main())
    delete_pid(pid_fname)
