# -*- coding:utf-8 -*-
import hashlib
from functools import wraps
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash, escape
from tao.models import *
from tao import utils
import logging
from urllib import unquote


app = Flask(__name__)
app.secret_key = '<$\xf4B@\xaa\x16\xfcZ2\x92\xfd^w\x10\xee\x97\x9c\xdb\xf5\xd8e\xc6\\'

def login_required(f):
    @wraps(f)
    def decorated_f(*args, **kwargs):
        if 'username' in session and session['username']:
            return f(*args, **kwargs)
        session['back'] = request.url
        return redirect(url_for('login'))
    return decorated_f

@app.route('/')
def index():
    try:
        page = int(request.args.get('page'))
    except:
        page = 1
    bs = Beike.all().order('-when').fetch(100, 10 * (page - 1))
    size = len(bs)
    return render_template('index.html', bs=bs)

@app.route('/like/<key>')
@login_required
def like(key):
    who = utils.get_current_user(session)
    url = Url.get(key)
    if url:
        like = Like.all().filter('url =',url).filter('who =' ,who).get()
        if request.args.get('unlike') == 'true':
            like.delete()
        elif not like:
            like = Like(url=url,who=who)
            like.put()
    return ''

@app.route('/view/<key>')
def view(key):
    url = Beike.get(key)
    who = utils.get_current_user(session)
    is_like = False
    if url and who:
        like = Like.all().filter('url =',url).filter('who =' ,who).get()
        if like:
            is_like = True
    return render_template('viewer.html',url=url,is_like=is_like)


@app.route('/tag/<tag>')
def view_by_tag(tag):
    try:
        page = int(request.args.get('page'))
    except:
        page = 1
    tag = unquote(tag)
    logging.error(tag)
    urls = Beike.all().filter('tags =', db.Key.from_path('Tag',tag)).order('-when').fetch(20, 20 * (page - 1))
    return render_template('index.html', urls=urls)

@app.route('/add')
@login_required
def add():
    url = request.args.get('url')
    if not url or not url.startswith('http://item.taobao.com'):
        return render_template('error.html', message='必须是淘宝的链接哦 ;-)'.decode('utf-8'))

    user = utils.get_current_user(session)
    beike = Beike.get_by_key_name(url)

    if not beike:
        title = utils.fetch_title(url)
        beike = Beike(key_name=url, title=title, digger=user)
        beike.put()

    flash('Whoa,you made it!')
    return redirect('/')

@app.route('/add/url/')
@login_required
def add_url():
    url = request.args.get('url')
    tags_param = request.args.get('tag')
    user = utils.get_current_user(session)
    tag_list = tags_param.split(' ')
    existing_url = Beike.get_by_key_name(url)
    is_existing = existing_url and True or False
    tag_keys = is_existing and existing_url.tags
    new_tag_keys = []
    for tag_name in tag_list:
        if tag_name:
            tag = Tag.new_or_get(tag_name, is_existing)
            if is_existing :
                if tag.key() not in tag_keys:
                    tag_keys.append(tag.key())
            new_tag_keys.append(tag.key())

    if not is_existing:
        existing_url = Beike(key_name=url, tags=new_tag_keys)
    else:
        existing_url.tags = tag_keys
    existing_url.put()

    existing_user_url = UserUrl.all().filter('who =', user).filter('url =', existing_url).get()
    if existing_user_url:
        existing_user_url.tags = new_tag_keys
    else:
        existing_user_url = UserUrl(who=user, url=existing_url, tags=new_tag_keys)
    existing_user_url.put()
    flash('Whoa,you made it!')
    return redirect('/')

@app.route('/login', methods=['GET', 'POST'])
def login():
  error = None
  if request.method == 'POST':
    if valid_login(request.form['username'],
                   request.form['password']):
      return log_the_user_in(request.form['username'])
    else:
      error = 'invalid password/username'
  return render_template('login.html')

def log_the_user_in(name):
  session['username'] = name
  if 'back' in session:
    if session['back']:
      return redirect(session['back'])
  return redirect('/')

def valid_login(name, pwd):
  user = User.all().filter('name =', name).get()
  if user:
    hashed = hashlib.sha1(pwd).hexdigest()
    if hashed == user.hashed_password:
      return user
    else:
      return False
  return False

@app.route('/logout')
def logout():
  if session['username']:
    session['username'] = None
    return redirect('/')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        if create_user(request.form['username'],
                       request.form['password'],
                       request.form['email']):
            session['username'] = request.form['username']
            return redirect('/')
    return render_template('signup.html')

def create_user(name, pwd, email):
    q = User.all().filter('name =', name)
    if q.count() == 0:
        user = User(name=name)
        user.hashed_password = hashlib.sha1(pwd).hexdigest()
        user.email = email
        user.put()
        return user
    else:
        return False



@app.route('/moo')
def moo():
    return render_template('moo.html')

