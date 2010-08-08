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

    def __unicode__(self):
        return self.name

    def __str__(self):
        return unicode(self).encode('utf-8')

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

class Beike(db.Model):
    url = db.StringProperty()
    when = db.DateTimeProperty(auto_now_add=True)
    tags = db.ListProperty(db.Key)
    title = db.StringProperty()


class UserUrl(db.Model):
    url = db.ReferenceProperty(Beike)
    who = db.ReferenceProperty(User)
    tags = db.ListProperty(db.Key)

class Activation(db.Model):
    user = db.ReferenceProperty(User)

class Like(db.Model):
    who = db.ReferenceProperty(User)
    url = db.ReferenceProperty(Beike)

