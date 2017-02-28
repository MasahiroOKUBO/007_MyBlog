from handlers import BaseHandler
from models import Post, comments_key
from google.appengine.ext import ndb


class EditComment(BaseHandler):
    """Login user can edit blog comments only which user posts."""
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
            message = "This is not your comment!"
            self.render("page-message.html", message=message)
            return
        self.render("form-edit-comment.html", comment=comment)
        return

    def post(self, post_id, comment_id):
        if not self.user:
            self.redirect('/login')
            return
        comment_key = ndb.Key('Comment', int(comment_id), parent=comments_key())
        comment = comment_key.get()
        author_id = comment.author_key.id()
        login_id = self.user.key.id()
        if not author_id == login_id:
            message = "This is not your post!"
            self.render("page-message.html", message=message)
            return
        comment.subject = self.request.get('subject')
        comment.content = self.request.get('content')
        if comment.subject and comment.content:
            comment.put()
            self.redirect('/blog/%s/comment/%s/show' % (post_id, comment_id))
            return
        else:
            error = "subject and content, please!"
            self.render("form-editcomment.html",
                        comment=comment,
                        error=error)
            return
