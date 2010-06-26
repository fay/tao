# -*- coding:utf-8 -*-
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
from tao.models import *
from tao import utils
import logging

from google.appengine.ext.webapp.util import login_required
app = Flask(__name__)
app.debug = True
app.secret_key = '<$\xf4B@\xaa\x16\xfcZ2\x92\xfd^w\x10\xee\x97\x9c\xdb\xf5\xd8e\xc6\\'

@app.route('/')
def index():
    try:
        page = int(request.args.get('page'))
    except:
        page = 1
    urls = Url.all().order('-when').fetch(20, 20 * (page - 1))
    return render_template('index.html', urls=urls)

@app.route('/tag/<tag>/')
def view_by_tag(tag):
    try:
        page = int(request.args.get('page'))
    except:
        page = 1
    urls = Url.all().filter('tags =', db.Key.from_path('Tag',tag)).order('-when').fetch(20, 20 * (page - 1))
    return render_template('index.html', urls=urls)

@login_required
@app.route('/add/url/1/')
def add_url_1():
    url_param = request.args.get('url')
    if not url_param or not url_param.startswith('http://item.taobao.com'):
        return render_template('error.html', message='必须是淘宝的链接哦 ;-)')

    user = None #= get_user()
    url = Url.get_by_key_name(url_param)
    if url and not url.title:
        title = utils.fetch_title(url_param)
        url.title = title
        url.put()

    tags = []
    if not url:
        title = utils.fetch_title(url_param)
        url = Url(key_name=url_param, tags=[], title=title)
        url.put()
    else:
        user_url = UserUrl.all().filter('who =', user).filter('url =', url).get()
        tags = (user_url and user_url.tags and user_url.tags) or []
    return render_template('add.html', url=url, tags=tags)

@login_required
@app.route('/add/url/')
def add_url():
    url_param = request.args.get('url')
    tags_param = request.args.get('tag')
    user = None#get_user()
    
    tag_list = tags_param.split(',')
    existing_url = Url.get_by_key_name(url_param)
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
        existing_url = Url(key_name=url_param, tags=new_tag_keys)
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