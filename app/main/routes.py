from app.main import main
from flask import current_app, jsonify, redirect, request, url_for, send_file, send_from_directory
from flask_login import current_user, login_required, login_user
from app.models import User, Post, List, Ranked_Member
from app.main.forms import RegistrationForm, EditProfileForm, PostForm, ResetPasswordRequestForm
from app.main.email import send_password_reset_email
from werkzeug.urls import url_parse
from datetime import datetime
from app import db

from random import choice

def redirectTo(route):
  return redirect(url_for(route))

@main.route('/')
@main.route('/index')
def index():
  form = PostForm()
  if form.validate_on_submit():
    post = Post(body=form.popst.data, author=current_user)
    db.session.add(post)
    db.session.commit()
    return redirect(url_for('index'))
  
  all = [{ 'name': user.username } 
    for user in User.query.all()]

  return jsonify(all)

@main.route('/teststatic')
def testStatic():
  return send_file('static/index.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
  if current_user.is_authenticated:
    return redirect(url_for('index'))
  form = RegistrationForm()
  user = User(username=form.username.data, email=form.email.data)
  user.set_password(form.password.data)
  db.session.add(user)
  db.session.commit()
  return 'You registered'

@main.route('/user/<username>')
def user(username):
  user = User.query.filter_by(username=username).join(List.list_members).first_or_404()

  lists = [
    { 'name': list.name, 'header': list.header }
    for list in user.playlists]

  reviews = [
    { 'name': review.restaurant.name, 'body': review.body }
    for review in user.reviews]

  payload = {
    'user': user.username,
    'lists': lists,
    'reviews': reviews }

  return jsonify(payload)

@main.route('/user/<username>/<playlist>')
def single_list(username, playlist):
  playlist = List.query.join(User).filter(User.username==username).first()
  return jsonify(playlist.name)

@main.route('/list/<creator_id>/<list_name>', methods=['POST'])
@login_required
def createFreshList(creator_id, list_name):
  upsert = List.query.filter_by(name=list_name, creator_id=creator_id).first()
  if not upsert:
    upsert = List(name=list_name, creator_id=creator_id)
  
  items = [Ranked_Member(restaurant_id=rank['restaurant_id'], hook=rank['hook'])
    for rank in request.json['ranks']]

  upsert.list_members.extend(items)
  db.session.add(upsert)
  db.session.commit()
  return 'new created'

@main.route('/listItem/<list_id>/<restaurant_id>', methods=['DELETE'])
def delete_member(list_id, restaurant_id):
  Ranked_Member.query.filter_by(list_id=list_id, restaurant_id=restaurant_id).delete()
  db.session.commit()
  return 'OK', 200

@main.route('/listItem/<list_id>', methods=['DELETE'])
def delete_list(list_id):
  List.query.get(list_id).delete()
  db.session.commit()
  return 'OK', 200
  
@main.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile(current_user):
  form = EditProfileForm()
  if form.validate_onsubmit():
    current_user.username = form.username.data
    current_user.about_me = form.about_me.data
    db.session.commit()
    return redirect(url_for('main.edit_profile'))

@main.before_request
def before_request():
  if current_user.is_authenticated:
    print('there is authed user')

@main.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        return 'no user'
    if user == current_user:
        return 'dont follow yourself'
    current_user.follow(user)
    db.session.commit()
    return redirect(url_for('main.user', username=username))

@main.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).frist()
    if user is None or user == current_user:
        print('failed to unfollow')
    current_user.unfollow(user)
    db.session.commit()
    return redirect(url_for('main.user', username=username))