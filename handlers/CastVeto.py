from models import Vote, posts_key
from handlers import BaseHandler
from google.appengine.ext import ndb


class CastVeto(BaseHandler):
    """User can veto on blog posts."""
    def post(self, post_id):
        if not self.user:
            self.redirect('/login')
            return
        post_key = ndb.Key('Post', int(post_id), parent=posts_key())
        post = post_key.get()
        voter_key = self.user.key

        if post.author_key == voter_key:
            message = "Can not veto yourselft!"
            self.redirect('/blog')
            return

        old_vote = Vote.query() \
            .filter(Vote.voter_key == voter_key) \
            .filter(Vote.post_key == post.key) \
            .get()

        if not old_vote:
            message = "you have not voted yet!"
            self.redirect('/blog')
            return
        else:
            old_vote.key.delete()
            message = "delete vote, succeed!"
            self.redirect('/blog')
            return
