from google.appengine.ext import ndb
import models.User
import Post


def votes_key(namespace='default'):
    return ndb.Key('votes', namespace)


class Vote(ndb.Model):
    voter_key = ndb.KeyProperty(kind=User)
    post_key = ndb.KeyProperty(kind=Post)
