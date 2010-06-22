# -*- coding: utf-8 -*-
from django.template import RequestContext
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from google.appengine.api import mail
from google.appengine.api import users
from appengine_django.auth.models import User
from google.appengine.ext import db
from google.appengine.api import memcache
from taolink.models import *
from taolink import session, utils
import logging, re
from datetime import datetime
from google.appengine.api.labs import taskqueue

PRIVILEGE_ERROR = 'Sorry,you don\'t have the privilege.'
RECENT_POST_SIZE = 5
_email = re.compile(r"[^@]+@[^@]+\.[^@]+")


def login(request):
    if get_user():
        return HttpResponseRedirect('/home/')
    if request.POST:
        email = request.POST.get('email', '')
        password = request.POST.get('password', None)
        user = User.all().filter('email = ', email).filter('password = ', password)
        if user.count() == 0:
            return render_to_response('login.html', {'login_error_email':'email或密码错误'}, context_instance=RequestContext(request))
        else:
            user = user.get()
        if not user.is_active:
            return render_to_response('login.html', {'login_error_activate':'该email地址还没有激活'}, context_instance=RequestContext(request))
        session['user'] = user
        return HttpResponseRedirect(request.GET.get('next', '') or request.GET.get('continue', '/'))
    by = request.GET.get('by')
    if by == 'google':
        return HttpResponseRedirect(users.create_login_url(request.GET.get('next', '') or request.GET.get('continue', '/')))

    confirm = request.GET.get('confirm')
    if confirm:
        success = True
        activation = memcache.get(confirm)
        if activation:
            session['user'] = activation.user
            activation.user.is_active = True
            activation.user.put()
            #从memcache中删除
            memcache.delete(confirm)
            #删除激活对象
            activation.delete()
        else:
            success = False
        return render_to_response('login.html', {'is_activation':True, 'is_activation_success':success, 'confirm':confirm}, context_instance=RequestContext(request))

    reconfirm = request.GET.get('reconfirm')
    if reconfirm:
        try:
            activation = Activation.get(reconfirm)
            _send_activate_mail(activation, request)
        except Exception, e:
            logging.error(e)
    return render_to_response('login.html', context_instance=RequestContext(request))

def register(request):
    if get_user():
        return HttpResponseRedirect('/home/')
    #如果是POST方式，则是执行注册操作
    if request.POST:
        email = request.POST.get('email', '')
        password = request.POST.get('password', None)
        if not _email.search(email):
            return render_to_response('login.html', {'error_email':'必须是有效的电子邮件地址', 'is_register':True}, context_instance=RequestContext(request))
        if len(password) < 6 or len(password) > 12:
            return render_to_response('login.html', {'error_password':'密码最好在6-12位，且须是数字和字母的组合', 'is_register':True}, context_instance=RequestContext(request))
        user = users.User(email)
        query = User.all().filter("user =", user)
        if query.count() == 0:
            django_user = User(user=user, password=password, is_active=False, email=user.email(), username=user.email())
            django_user.save()
            activation = Activation(user=django_user)
            activation.save()
            _send_activate_mail(activation, request)
        else:
            return render_to_response('login.html', {'error_email':'这个Email地址已经在使用了', 'is_register':True}, context_instance=RequestContext(request))
        return render_to_response('login.html', {'is_register':True, 'register_success':True}, context_instance=RequestContext(request))
    #如果是GET方式，即是请求注册页面
    return render_to_response('login.html', {'is_register':True}, context_instance=RequestContext(request))

"""
发送激活邮件
"""
def _send_activate_mail(activation, request) :   
        django_user = activation.user
        # 一个小时过期
        memcache.add(activation.key().__str__(), activation, 60 * 60)
        logging.error(activation.key().__str__())
        mail.send_mail(sender="toozoofoo@gmail.com", to=django_user.email, subject="欢迎加入Friendbeat!", body="复制此链接到浏览器中激活您的帐号:http://" + request.get_host() + "/accounts/login/?confirm=" + activation.key().__str__(), html="<a target=\"_blank\" href=\"http://" + request.get_host() + "/accounts/login/?confirm=" + activation.key().__str__() + "\">请点击此链接激活您的账户</a>")

def logout(request):
    if users.get_current_user():
        return HttpResponseRedirect(users.create_logout_url('/'))
    user = session.get('user', None)
    if user:
        del(session['user'])
    return HttpResponseRedirect('/')


@login_required
def watch(request, user_name):
    user = get_user()
    watched_user = User.all().filter('username', user_name).get()
    watch = Watch(watcher=user, watched=watched_user)
    not_existed = watch.create()
    if not_existed:
        m = 'ok'
    else:
        m = 'watched'
    return HttpResponse(m)

@login_required
def unwatch(request, user_name):
    user = get_user()
    watched_user = User.all().filter('username', user_name).get()
    watch = Watch.all().filter('watcher = ' , user).filter('watched = ' , watched_user).get()
    watch.delete()
    return HttpResponse("")

    



def index(request):
    try:
        page = int(request.GET['page'])
    except:
        page = 1
    try:
        urls = Url.all().order('-when').fetch(20, 20 * (page - 1))
    except IndexError, e:
        urls = []
    
    is_last = len(urls) < 20
    paginator = utils.createPaginator(page, is_last)
    return render_to_response('index.html', {'urls':urls,
                                               'paginator':paginator},
                                                context_instance=RequestContext(request))

@login_required
def add_url_1(request):
    url_param = request.GET.get('url')
    if not url_param or not url_param.startswith('http://item.taobao.com'):
        return render_to_response('error.html', {'message':'必须是淘宝的链接哦 ;-)'}, context_instance=RequestContext(request))

    user = get_user()
    url = Url.get_by_key_name(url_param)
    if url and not url.title:
        title = utils.fetch_title(url_param)
        url.title = title
        url.put()

    tags = []
    if not url:
        title = utils.fetch_title(url_param)
        url = Url(key_name=url_param, tags=[],title=title)
        url.put()
    else:
        user_url = UserUrl.all().filter('who =', user).filter('url =', url).get()
        tags = user_url and user_url.tags
    return render_to_response('add.html', {'url':url,'tags':tags}, context_instance=RequestContext(request))

    
@login_required
def add_url(request):
    url_param = request.GET.get('url')
    tags_param = request.GET.get('tag')
    user = get_user()
    
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
    
    return HttpResponseRedirect('/')

"""
得到自定义的User Model
"""
def get_user():
    who = users.get_current_user()
    if who:
        #django user
        user = User.all().filter('user = ', who).get()
    else:
        user = session.get('user')
    return user




def cron_daily_stat(request):
    taskqueue.Task(url='/work/daily_stat/').add(queue_name='dailystat')
    return HttpResponse()

def daily_stat(request):
    current_time = datetime.today()
    today_start = datetime(current_time.year, current_time.month, current_time.day)
    yesterday_start = datetime(current_time.year, current_time.month, current_time.day - 1)

    users = User.all().fetch(1000)
    for user in users:
        count = UserUrl.all().filter('who = ', user).filter('when < ', today_start.date()).filter('when > ', yesterday_start.date()).count()
        #stat = ActStat(who=user, count=count, when=today_start.date())
        #stat.save()

    return HttpResponse()

def about(request):
    return HttpResponse("")

