from models import Vote, comments_key, votes_key
from handlers import BaseHandler
from google.appengine.ext import ndb


class DeleteComment(BaseHandler):
    def get(self, post_id, comment_id):
        if not self.user:
            self.redirect('/login')
            return

        comment_key = ndb.Key('Comment', int(comment_id), parent=comments_key())
        comment = comment_key.get()
        if not comment:
            self.error(404)
            return

        author_id = comment.author_key.id()
        login_id = self.user.key.id()
        if not author_id == login_id:
            message = "This is not your post!"
            self.render("page-message.html", message=message)
            return

        self.render("form-delete-comment.html", c=comment)

    def post(self, post_id, comment_id):
        if not self.user:
            self.redirect('/login')
            return
        comment_key = ndb.Key('Comment', int(comment_id), parent=comments_key())
        comment = comment_key.get()

        author_id = comment.author_key.id()
        login_id = self.user.key.id()
        if not author_id == login_id:
            message = "This is not your comment!"
            self.render("page-message.html", message=message)
            return

        if comment:
            comment.key.delete()
            message = "Delete succeeed!"
            self.render("page-message.html", message=message)
        else:
            error = "post does not exists!"
            self.render("page-message.html", message=error)

