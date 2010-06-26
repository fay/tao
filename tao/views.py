# -*- coding:utf-8 -*-
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
from tao.models import *
from tao import utils
from google.appengine.ext.webapp.util import login_required
app = Flask(__name__)
app.debug = True

@app.route('/')
def index():
    try:
        page = int(request.args.get('page'))
    except:
        page = 1
    urls = Url.all().order('-when').fetch(20, 20 * (page - 1))
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
        tags = user_url and user_url.tags
    return render_template('add.html', url=url, tags=tags)
