from run import *
import holidays
import datetime as dt
import requests
import json
from pandas_datareader import data
import time
import matplotlib.pyplot as plt



def next_business_day(date):
    us_holidays = holidays.US()
    next_day    = date + dt.timedelta(1)
    if next_day.weekday() in (5, 6) or next_day in us_holidays or next_day in set([dt.datetime(2017, 4, 14)]):
        next_day = next_business_day(next_day)
    return next_day

def previous_business_day(date):
    us_holidays = holidays.US()
    previous_day    = date - dt.timedelta(1)
    if previous_day.weekday() in (5, 6) or previous_day in us_holidays or previous_day in set([dt.datetime(2017, 4, 14)]):
        previous_day = previous_business_day(previous_day)
    return previous_day

class portfolio_contructor(object):
    def __init__(self, subr, cred_path, save_dir=None, cutoff=0.01):
        self.subr      = subr
        self.cred_path = cred_path
        self.save_dir  = save_dir
        self.cutoff    = cutoff

        self.cache = {}

    def get_raw_exposure_df(self, d0, d1):

        result = []
        ticker_list = make_ticker_list()

        s = SubScraper(self.cred_path)
        d = d0

        while d < d1:
            if d in self.cache:
                result += self.cache[d]
                d += dt.timedelta(1)
            else:
                print('collecting submissions for ' + str(d.date()))
                r = []
                submissions = s.get_submissions_between(self.subr, str(d.date()), str((d + dt.timedelta(1)).date()))

                for sub in submissions:
                    r.append(process_submission(sub, ticker_list))

                self.cache[d] = r
                result += self.cache[d]
                d += dt.timedelta(1)
                time.sleep(1)

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

        if self.save_dir is not None:
            df.to_csv(self.save_dir + 'agged_data_{0}_{1}.csv'.format(str(d0.date()), str(d1.date())))

        df['date'] = pd.to_datetime(df['date'])

        return df

    def create_portfolio(self, rdf):
        tickers = rdf['ticker'].unique()
        dates   = rdf['date'].unique()

        tdf = pd.DataFrame(columns=tickers, index=dates)

        for t in tickers:
            for d in dates:

                e = rdf[(rdf['ticker'] == t) & (rdf['date'] == d)]

                if len(e) > 0:
                    tdf.loc[d, t] = e['exposure'].iloc[0]
                else:
                    tdf.loc[d, t] = 0
        
        sdf = pd.ewma(tdf, span=len(tdf) - 1)
        rp  = sdf.iloc[-1]

        for t in rp.index:
            if rp.loc[t] < self.cutoff:
                rp.drop(t, inplace=True)

        rp = rp / sum(rp)

        return rp

    def drop_ticker(self, s, t):
        s.drop([t], inplace=True)
        s = s / s.sum()
        return s

    def drop_tickers(self, pdict, dl):
        for day in pdict:
            for t in (pdict[day]).index:
                if t in dl:
                    pdict[day] = self.drop_ticker(pdict[day], t)
        return pdict

    def get_portfolio(self, tdate, lookback):
        d0  = tdate - dt.timedelta(lookback)
        rdf = self.get_raw_exposure_df(d0, tdate)
        p   =  self.create_portfolio(rdf)

        return p

    def get_portfolio_dict(self, d0, d1, lookback):
        pdict = {}
        d = d0
        while d < d1:
            pdict[next_business_day(d)] = self.get_portfolio(d, lookback)
            d = next_business_day(d)

        return pdict

    def get_ticker_list(self, pdict):
        tlist = []

        for d in pdict:
            for t in pdict[d].index:
                if t not in tlist: tlist.append(t)

        return tlist

    def get_close_price_dict(self, d0, d1, tickers):
        cpdict, droplist = {}, []

        for t in tickers:
            try:
                cpdict[t] = data.DataReader(t, 'quandl', d0, next_business_day(d1), retry_count=1, pause=0.05)
                cpdict[t].index  = pd.to_datetime((cpdict[t]).index)
                print('collected ' + t)

            except:
                print('dropped ' + t)
                droplist.append(t)

            time.sleep(3)

        return cpdict, droplist

    def get_portfolio_change(self, pdict, cpdict):
        idict = {}

        for day in pdict:
            pdict[day] = pdict[day].to_frame()
            pdict[day].columns = ['weight']

            for t in (pdict[day]).index:
                try:
                    p0 = (cpdict[t]).loc[previous_business_day(day), 'AdjClose']
                    p1 = (cpdict[t]).loc[day, 'AdjClose']

                    (pdict[day])['pct_change'] = (p1 - p0) / p0
                except:

                    def drop_ticker(self, df, t):
                        df.drop([t], inplace=True)
                        df['weight'] = df['weight'] / df['weight'].sum()
                        return df

                    pdict[day] = drop_ticker(pdict[day], t)

            idict[day] = sum((pdict[day])['weight'] * (pdict[day])['pct_change'])

        return pdict, idict



if __name__ == '__main__':
    subr = 'wallstreetbets'
    cp   = 'C:/Users/Owner.DESKTOP-UT1NOGO/Desktop/python/wsb-master/dev/credentials.txt'
    pc   = portfolio_contructor(subr, cp, cutoff=0.02)
    
    d0 = dt.datetime(2017, 7, 3)
    d1 = dt.datetime(2017, 8, 3)

    pdict   = pc.get_portfolio_dict(d0, d1, 20)
    tlist   = pc.get_ticker_list(pdict)

    print(tlist)
    cpdict, dl = pc.get_close_price_dict(d0, d1, tlist)

    pdict = pc.drop_tickers(pdict, dl)

    pdict, idict = pc.get_portfolio_change(pdict, cpdict)

    i = [69]
    for d in idict:
        i.append(i[-1] * (idict[d] + 1))

    plt.plot(list(idict.keys()), i[1:])
    plt.show()
