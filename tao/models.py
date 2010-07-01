# -*- coding: utf-8 -*-
from google.appengine.ext import db

class User(db.Model):
    name = db.StringProperty(required=True)
    first_name = db.StringProperty()
    last_name = db.StringProperty()
    email = db.EmailProperty()
    hashed_password = db.StringProperty()
    is_staff = db.BooleanProperty(default=False, required=True)
    is_active = db.BooleanProperty(default=True, required=True)
    is_superuser = db.BooleanProperty(default=False, required=True)
    last_login = db.DateTimeProperty(auto_now_add=True, required=True)
    date_joined = db.DateTimeProperty(auto_now_add=True, required=True)

class Tag(db.Model):
    #tag = db.StringProperty()
    num = db.IntegerProperty(default=0)
    @classmethod
    def new_or_get(cls, tag_name, is_new_url=True):
        tag = Tag.get_or_insert(tag_name)
        if is_new_url:
            tag.num = tag.num + 1
            tag.put()
        return tag

class Url(db.Model):
    #url = db.StringProperty()
    when = db.DateTimeProperty(auto_now_add=True)
    tags = db.ListProperty(db.Key)
    title = db.StringProperty()


class UserUrl(db.Model):
    url = db.ReferenceProperty(Url)
    who = db.ReferenceProperty(User)
    tags = db.ListProperty(db.Key)

class Activation(db.Model):
    user = db.ReferenceProperty(User)

class Watch(db.Model):
    watcher = db.ReferenceProperty(User, collection_name="watcher_set")
    watched = db.ReferenceProperty(verbose_name="watched", collection_name="watched_set", reference_class=User)

    def create(self):
        if self.watched.key() == self.watcher.key():
            return False
        existing_watch = Watch.all().filter('watcher = ', self.watcher).filter('watched = ', self.watched).get()
        if existing_watch:
            return False
        else:
            self.put()
            return True

