'''
Created on Apr 5, 2010

@author: b
'''
from django.contrib.auth.models import AnonymousUser

from google.appengine.api import users
from taolink import session
from appengine_django.auth.models import User
class LazyUser(object):
  def __get__(self, request, obj_type=None):
    if not hasattr(request, '_cached_user'):
      user = users.get_current_user()
      if user:
        request._cached_user = User.get_djangouser_for_user(user)
      else:
        user = session.get('user', None)
        if user:
            request._cached_user = user
        else:
            request._cached_user = AnonymousUser()
    return request._cached_user


class AuthenticationMiddleware(object):
  def process_request(self, request):
    request.__class__.user = LazyUser()
    return None