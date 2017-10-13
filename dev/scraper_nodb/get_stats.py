# take submission and standardize
# data points ticker, weight, sentiment

from match_tickers import SymbolFinder
import datetime as dt

def unix_to_string(s, format):
    return dt.datetime.fromtimestamp(s).strftime(format)

def unix_to_datetime(s):
    return dt.datetime.strptime(unix_to_string(s, '%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')

def cst1500(d):
    return dt.datetime.combine(d.date(), dt.datetime(1990, 1, 1, 15).time())

class Post:

    def __init__(self, submission):
        self.submission = submission
        
        tcst = unix_to_datetime(submission.created) - dt.timedelta(hours=6)

        if tcst > cst1500(tcst):
            # self.date = unix_to_string(tcst + dt.timedelta(1), '%Y-%m-%d')
            self.date = str((tcst + dt.timedelta(1)).date())
        else:
            # self.date = unix_to_string(tcst, '%Y-%m-%d')
            self.date = str(tcst.date())

        self.create_text()

    def create_text(self):
        self.text = self.submission.title + self.submission.selftext

    def calculate_ticker(self, ticker_list, dollar_sign=False):
        finder = SymbolFinder(ticker_list, dollar_sign)
        self.ticker = finder.get_primary_ticker(self.text)

    def calculate_sentiment(self):
        self.sentiment = 1

    def calculate_exposure(self):
        self.exposure = self.submission.ups + 2*self.submission.num_comments

    def get_stats(self, ticker_list, dollar_sign=False):
        self.calculate_ticker(ticker_list, dollar_sign)
        self.calculate_sentiment()
        self.calculate_exposure()

