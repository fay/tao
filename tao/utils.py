# -*- coding: utf-8 -*-
from google.appengine.api import urlfetch
import urllib
import logging,re

from google.appengine.api.labs import taskqueue
PAGE_SIZE = 10

def createPaginator(page,is_last):
    paginator = ''
    if page != 1:
        paginator += '<a href=\"?page=' + str(page - 1) + '\">‹ Pre</a> '
    paginator += 'Page ' + str(page) + ' '
    if not is_last:
        paginator += '<a href=\"?page=' + str(page + 1) + '\">Next ›</a>'
    return paginator

def standard_ratio(max_value, min_value, value):
    offset = max_value - min_value
    if offset > 110:
        ratio = offset / 110.0
        return value / ratio
    else:
        return value 
    


"""
是否为开发环境
"""
def is_debug(host):
    if host.startswith('127.0.0.1') or host.startswith('localhost'):
        return  True
    return False

def fetch_title(url):
    result = urlfetch.fetch(url=url, method=urlfetch.GET)
    if result.status_code != 200:
        logging.error(result.content)
        return ''
    else:
        for line in result.content.split("\n"):
            title = re.findall('<title>([^<]*)</title>',line)
            if title:
                logging.error(title[0])
                return title[0].decode('GBK')
    return ''

def publish(host, topic):
    DEBUG = is_debug(host)
    publish_form = {
      "hub.mode": "publish",
      "hub.url":topic
    }
    publish_data = urllib.urlencode(publish_form)
    publish_url = (DEBUG and 'http://localhost:8080/publish') or 'http://dragon-sea.appspot.com/publish'
    result = urlfetch.fetch(url=publish_url,
                            payload=publish_data,
                            method=urlfetch.POST,
                            headers={'Content-Type': 'application/x-www-form-urlencoded'})

    if result.status_code != 204 :
        logging.error('publish topic:' + topic + 'error,details:' + result.content)
        return False
    return True