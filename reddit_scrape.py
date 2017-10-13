import praw
from reddit_db import db, post, comment

db.create_all()

reddit = praw.Reddit(client_id='',
                     client_secret='',
                     password='',
                     user_agent='testscript by ya boi',
                     username='')


#Changing the limit will change amount posts recieved
#Can change .hot to ".top", ".rising", ".new", etc
#Changing .subreddit input will change the subreddit that is scraped becuase duh
submissions = reddit.subreddit('wallstreetbets').hot(limit=5)

for submission in submissions:
	try:
		p =  post(
				rid = submission.id
				,created = submission.created
				,author = str(submission.author)
				,title = submission.title
				,selftext = str(submission.selftext.decode('utf-8'))
				,num_comments = submission.num_comments
				,score = submission.score
				)

		db.session.add(p)
		db.session.commit()
	except Exception,e:
		print str(e)
		pass

	submission.comments.replace_more(limit=0)
	for comm in submission.comments.list():
		try:
			c = comment(
				rid = comm.id
				,created = comm.created
				,author = str(comm.author)
				,body = str(comm.body.decode('utf-8'))
				,score = comm.score
				,original_post = p
				)
			db.session.add(c)
			db.session.commit()
		except Exception,e:
			print str(e)
			pass
		