from models import Post, comments_key, Comment
from handlers import BaseHandler
from google.appengine.ext import ndb


class ShowComment(BaseHandler):
    def get(self, post_id, comment_id):
        comment_key = ndb.Key('Comment', int(comment_id), parent=comments_key())
        comment = comment_key.get()
        if not comment:
            self.error(404)
            return
        self.render("page-blog-comment.html",
                    c=comment,
                    post_id=post_id,
                    comment_id=comment_id)
        return

