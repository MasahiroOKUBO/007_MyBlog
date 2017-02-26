from handlers import BaseHandler
from models import Post, posts_key
from google.appengine.ext import ndb


class EditPost(BaseHandler):
    def get(self, post_id):
        if not self.user:
            self.redirect('/login')
            return

        key = ndb.Key('Post', int(post_id), parent=posts_key())
        post = key.get()

        if not post:
            self.error(404)
            return

        print post.author_key
        author_id = post.author_key.id()
        login_id = self.user.key.id()
        print author_id
        print login_id
        if not author_id == login_id:
            message = "This is not your post!"
            self.render("page-message.html", message=message)
            return

        self.render("form-edit-post.html", p=post)

    def post(self, post_id):
        if not self.user:
            self.redirect('/login')
            return
        post_key = ndb.Key('Post', int(post_id), parent=posts_key())
        post = post_key.get()
        author_id = post.author_key.id()
        login_id = self.user.key.id()
        if not author_id == login_id:
            message = "This is not your post!"
            self.render("page-message.html", message=message)
            return
        key = ndb.Key('Post', int(post_id), parent=posts_key())
        post = key.get()
        post.subject = self.request.get('subject')
        post.content = self.request.get('content')

        if post.subject and post.content:
            post.put()
            self.redirect('/blog/%s/show' % str(post.key.id()))
        else:
            error = "subject and content, please!"
            self.render("form-editpost.html",
                        subject=post.subject,
                        content=post.content,
                        error=error)
