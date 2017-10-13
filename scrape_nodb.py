import praw
import time
import datetime


def string_to_unix(s, format):
    return time.mktime(datetime.datetime.strptime(s, format).timetuple())


class SubScraper:
    def __init__(self, cred_file):
        with open(cred_file, 'r') as f:
            creds = [x.strip() for x in f]

        self.R = praw.Reddit(client_id=creds[0],
                             client_secret=creds[1],
                             password=creds[2],
                             user_agent='testscript by ya boi',
                             username='wsbIndex')

    def get_submissions_between(self, subreddit, start_date, end_date):
        sdate_unix = string_to_unix(start_date, '%Y-%m-%d')
        edate_unix = string_to_unix(end_date, '%Y-%m-%d')
        submissions = self.R.subreddit(subreddit).submissions(sdate_unix, edate_unix)
        return submissions