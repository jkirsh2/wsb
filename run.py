import pandas as pd
from get_stats import Post
from scrape_nodb import SubScraper

start_date = '2017-01-01'
end_date = '2017-10-01'
subr = 'wallstreetbets'

def make_ticker_list(filters = []):
    raw = list(pd.read_csv('../../data/nyse.csv').Symbol) + list(pd.read_csv('../../data/nasdaq.csv').Symbol)
    without_bs = [x.strip() for x in raw if '^' not in x]
    return [x for x in without_bs if x not in filters]


def process_submission(s, ticker_list):
    one_p = Post(s)
    one_p.get_stats(ticker_list, dollar_sign=True)
    return (one_p.date, one_p.ticker, one_p.sentiment, one_p.exposure)

if __name__ == '__main__':
    result = []
    ticker_list = make_ticker_list()
    s = SubScraper('C:/Users/Owner.DESKTOP-UT1NOGO/Desktop/python/wsb-master/dev/credentials.txt')
    submissions = s.get_submissions_between(subr, start_date, end_date)

    for s in submissions:
        result.append(process_submission(s, ticker_list))

    df = pd.DataFrame(result, columns = ['date', 'ticker', 'sentiment', 'exposure'])
    df = df.groupby(['date', 'ticker']).agg({'sentiment':'mean', 'exposure':'sum'}).reset_index()
    df_totalexposure = (df
                        .groupby('date')
                        .agg({'exposure':sum})
                        .rename(columns = {'exposure':'daily_exposure'})
                        .reset_index()
                        )

    df = df.merge(df_totalexposure, on='date', how='left')
    df['exposure'] = df['exposure']/df['daily_exposure']
    df = df.drop('daily_exposure', axis=1)
    df.to_csv('agged_data_{0}_{1}.csv'.format(start_date, end_date))