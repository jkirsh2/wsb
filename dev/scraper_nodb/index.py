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
    if next_day.weekday() in (5, 6) or next_day in us_holidays:
        next_day = next_business_day(next_day)
    return next_day


class portfolio_contructor(object):
	def __init__(self, subr, cred_path, save_dir=None, cutoff=0.02):
		self.subr      = subr
		self.cred_path = cred_path
		self.save_dir  = save_dir
		self.cutoff    = cutoff

	def get_raw_exposure_df(self, d0, d1):
	    result = []
	    ticker_list = make_ticker_list()

	    s = SubScraper(self.cred_path)
	    submissions = s.get_submissions_between(self.subr, str(d0.date()), str(d1.date()))

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

	def drop_ticker(self, df, t):
		df.drop([t], inplace=True)
		df['weight'] = df['weight']/df['weight'].sum()
		return df

	def get_portfolio(self, tdate, lookback):
		d0  = tdate - dt.timedelta(lookback)
		rdf = self.get_raw_exposure_df(d0, tdate)
		p   =  self.create_portfolio(rdf)

		df = pd.DataFrame(index=p.index, columns=['weight', 'pct_change'])

		df['weight'] = p

		d1 = next_business_day(tdate)
		print(d1)
		print(p.index)
		for t in p.index:
			try:
				sdata = data.DataReader(t, 'quandl', tdate, d1)
				# time.sleep(3)
				while len(sdata) <= 1:
					d1 += dt.timedelta(1)
					sdata = data.DataReader(t, 'quandl', tdate, d1)
				df.loc[t, 'pct_change'] = (sdata['AdjClose'].iloc[-2] - sdata['AdjClose'].iloc[-1])/sdata['AdjClose'].iloc[-1]
			except:
				df = self.drop_ticker(df, t)
		return df, sdata.index[-2]


if __name__ == '__main__':
	subr = 'wallstreetbets'
	cp   = 'C:/Users/Owner.DESKTOP-UT1NOGO/Desktop/python/wsb-master/dev/credentials.txt'
	pc   = portfolio_contructor(subr, cp, cutoff=0.05)
	
	pdict = {}
	cdict = {}

	i  = [69]

	d0 = dt.datetime(2017, 1, 3)
	d1 = dt.datetime(2017, 1, 6)

	while d0 < d1:
		p, d0 = pc.get_portfolio(d0, 3)
		print(d0)
		print(p.sort_values('weight', ascending=False))
		pdict[d0] = p
		pchange   = sum(p['weight'] * p['pct_change'])
		cdict[d0] = pchange
		i.append(i[-1] * (1+ pchange))
		print(pchange, i[-1])

	print(i[1:], cdict.keys())
	plt.plot(list(cdict.keys()), i[1:])
	plt.show()


	# aapl = data.DataReader('AMD', 'quandl', d0, d1)
	# print(aapl.head())
	# print(aapl.tail())
