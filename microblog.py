import click
from app import db, create_app
from app.models import User, Post, Restaurant, Review, List, Ranked_Member


app = create_app()

@app.shell_context_processor
def make_shell_context():
  return { 'db': db, 'User': User, 'Post': Post, 'addMarcos': addMarcos, 'List': List }

@app.cli.command("setup:flaskenv")
def setup_flaskenv():
  file = open('.fart', 'w+')
  keys = [
    'FLASK_APP=microblog.py', 
    'FLASK_DEBUG=',
    'SECRET_KEY=',
    'MAIL_SERVER=',
    'MAIL_PORT=',
    'MAIL_USER_TLS=',
    'MAIL_USERNAME=']
  
  file.write('\n'.join(keys))
  file.close()

def addMarcos():
  u = User(username='Marcos', email='mv@mv.com', password_hash='nba')
  db.session.add(u)
  restaurant = Restaurant(name='jajaja')
  review = Review(body='Awesome burritos', user_id=1, restaurant_id=1)
  playlist = List(name='Best plant based', header='yum', creator_id=1)
  ranked = Ranked_Member(ranking=5, hook='best east broadway', list_id=1, restaurant_id=1)

  db.session.add(restaurant)
  db.session.add(review)
  db.session.add(playlist)
  db.session.add(ranked)

  db.session.commit()