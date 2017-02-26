from handlers import BaseHandler
from google.appengine.ext import ndb
from models import posts_key, Comment

class ShowPost(BaseHandler):
    def get(self, post_id):
        key = ndb.Key('Post', int(post_id), parent=posts_key())
        post = key.get()
        comments = Comment.query() \
            .filter(Comment.post_key == key) \
            .order(-Comment.created) \
            .fetch(10)
        if not post:
            self.error(404)
            return
        self.render("page-blog-post.html",
                    p=post,
                    post_id=post_id,
                    comments=comments)
        return

