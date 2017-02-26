from handlers import BaseHandler
from models import Post, posts_key
from google.appengine.ext import ndb


class DeletePost(BaseHandler):
    def get(self, post_id):
        if not self.user:
            self.redirect('/login')
            return

        key = ndb.Key('Post', int(post_id), parent=posts_key())
        post = key.get()
        if not post:
            self.error(404)
            return

        author_id = post.author_key.id()
        login_id = self.user.key.id()
        if not author_id == login_id:
            message = "This is not your post!"
            self.render("page-message.html", message=message)
            return

        self.render("form-delete-post.html", p=post)

    def post(self, post_id):
        if not self.user:
            self.redirect('/login')
            return

        key = ndb.Key('Post', int(post_id), parent=posts_key())
        post = key.get()

        author_id = post.author_key.id()
        login_id = self.user.key.id()
        if not author_id == login_id:
            message = "This is not your post!"
            self.render("page-message.html", message=message)
            return

        if post:
            post.key.delete()
            message = "Delete succeeed!"
            self.render("page-message.html", message=message)
        else:
            error = "post does not exists!"
            self.render("page-message.html", message=error)
