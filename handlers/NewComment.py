from models import Post, comments_key, Comment, posts_key
from handlers import BaseHandler
from google.appengine.ext import ndb


class NewComment(BaseHandler):
    """User can add new comment on post."""
    def get(self, post_id):
        if not self.user:
            self.redirect("/login?redirectUrl=/blog/%s/comment/new" % post_id)
            return
        else:
            self.render("form-new-comment.html")
            return

    def post(self, post_id):
        if not self.user:
            self.redirect('/blog')
            return
        subject = self.request.get('subject')
        content = self.request.get('content')
        author_key = self.user.key
        post_key = ndb.Key('Post', int(post_id), parent=posts_key())
        if not subject and content:
            error = "subject & content, please!"
            self.render("form-new-comment.html",
                        subject=subject,
                        content=content,
                        error=error)
            return
        else:
            comment = Comment(parent=comments_key(),
                              subject=subject,
                              content=content,
                              author_key=author_key,
                              post_key=post_key)
            comment.put()
            self.redirect('/blog')
            return

