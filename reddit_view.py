from reddit_db import db, post, comment

db.create_all()

posts = post.query.all()

for p in posts:
	print "POST~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
	print "reddit_id: " + str(p.rid) + " created_utc: " + str(p.created) + " author: " + p.author 
	print "num_comments: " + str(p.num_comments) + " score :" + str(p.score)
	print "title: " + p.title
	print "selftext: " + p.selftext
	print "Comments~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"

	for c in p.comments:
		print "reddit_id: " + str(c.rid) + " created_utc: " + str(c.created) + " author: " + c.author 
		print "score: " + str(c.score)
		print "body: " + c.body
		print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
