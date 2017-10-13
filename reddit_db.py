from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/reddit_v1.db'
db = SQLAlchemy(app)

class post(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	rid = db.Column(db.String(100), unique=True)
	created = db.Column(db.Integer, unique=False)
	author = db.Column(db.String(255), unique=False)
	title = db.Column(db.Text, unique=False)
	selftext = db.Column(db.Text, unique=False)
	num_comments = db.Column(db.Integer, unique=False)
	score = db.Column(db.Integer, unique=False)
	comments = db.relationship('comment', backref='original_post', lazy='dynamic')
	
	def __init__(self,rid,created,author,title,selftext,num_comments,score):
		self.rid = rid
		self.created = created
		self.author = author
		self.title = title
		self.selftext = selftext
		self.num_comments = num_comments
		self.score = score

	def __repr__(self):
		return '<title %r>' % self.title + " " +  str(self.score) 

class comment(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	rid = db.Column(db.String(100), unique=True)
	created = db.Column(db.Integer, unique=False)
	author = db.Column(db.String(255), unique=False)
	body = db.Column(db.Text, unique=False)
	score =  db.Column(db.Integer, unique=False)
	post_id = db.Column(db.Integer, db.ForeignKey('post.id'))

	def __init__(self,rid,created,author,body,score,original_post):
		self.rid = rid
		self.created = created
		self.author = author
		self.body = body
		self.score = score
		self.original_post = original_post

	def __repr__(self):
		return '<title %r>' % self.author + " " +  str(self.body) + " " + str(self.score)






