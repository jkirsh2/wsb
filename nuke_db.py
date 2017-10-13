from reddit_db import db, post, comment

posts =  post.query.all()

comments = comment.query.all()

for p in posts:
	db.session.delete(p)
	
for c in comments:
	db.session.delete(c)

db.session.commit()
