from handlers import BaseHandler
from models import Post, posts_key


class NewPost(BaseHandler):
    def get(self):
        if self.user:
            self.render("form-new-post.html")
            return
        else:
            self.redirect("/login")
            return

    def post(self):
        if not self.user:
            self.redirect('/blog')

        subject = self.request.get('subject')
        content = self.request.get('content')
        author_key = self.user.key

        if subject and content:
            p = Post(parent=posts_key(), subject=subject, content=content, author_key=author_key)
            p.put()
            self.redirect('/blog/%s/show' % str(p.key.id()))
            return
        else:
            error = "subject and content, please!"
            self.render("form-new-post.html", subject=subject, content=content, error=error)
            return
