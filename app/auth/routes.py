from app.auth import auth
from app.auth.forms import LoginForm
from flask_login import current_user, login_required, login_user, logout_user
from flask import redirect, request, url_for, render_template, flash
from werkzeug.urls import url_parse

def redirectTo(route):
  return redirect(url_for(route))

@auth.route('/logout')
def logout():
  logout_user()
  return redirect(url_for('main.index'))

@auth.route('/login', methods=['GET', 'POST'])
def login():
  if current_user.is_authenticated:
    return redirect(url_for('main.index'))
  form = LoginForm()
  if form.validate_on_submit():
    user = User.query.filter_by(username=form.username.data).first()
    if user is None or not user.check_check_password(form.password.data):
      flash('invalid pass')
      return redirect(url_for('auth.login'))
    login_user(user, remember=form.remember_me.data)
    next_page = request.args.get('next')
    if not next_page or url_parse(next_page).netloc != '':
      next_page = url_for('main.index')
    return redirect(url_for('main.index'))
  return 'YOU LOGGED IN'

@auth.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('auth.login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)

@auth.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
  if current_user.is_authenticated:
    return redirect(url_for('main.index'))
  user = User.verify_reset_password_token(token)
  if not user:
    return redirectTo('main.index')
  form = ResetPasswordRequestForm()
  if form.validate_on_submit():
    user.set_password(form.password.data)
    db.session.commit()
    return redirectTo('auth.login')
  return 'do you want to reset passwrod?'