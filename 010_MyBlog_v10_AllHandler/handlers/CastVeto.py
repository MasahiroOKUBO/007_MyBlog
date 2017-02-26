from models import Vote, posts_key
from handlers import BaseHandler
from google.appengine.ext import ndb


class CastVeto(BaseHandler):
    def post(self, post_id):
        if not self.user:
            self.redirect('/login')
            return

        post_key = ndb.Key('Post', int(post_id), parent=posts_key())
        post = post_key.get()

        voter_key = self.user.key

        old_vote = Vote.query() \
            .filter(Vote.voter_key == voter_key) \
            .filter(Vote.post_key == post.key) \
            .get()

        if not old_vote:
            message = "you have not voted yet!"
            self.render("page-message.html", message=message)
            return
        else:
            old_vote.key.delete()
            message = "delete vote, succeed!"
            self.render("page-message.html", message=message)
            return
