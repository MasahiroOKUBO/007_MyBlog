from models import Post
from handlers import BaseHandler


class BlogFront(BaseHandler):
    """Make Blog top page."""
    def get(self):
        flash_message = self.request.get('flash_message')
        posts = Post.query().order(-Post.created)
        self.render('page-blog-top.html',
                    posts=posts,
                    flash_message=flash_message)
