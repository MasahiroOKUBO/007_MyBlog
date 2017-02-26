from models import Post
from handlers import BaseHandler


class BlogFront(BaseHandler):
    def get(self):
        posts = Post.query().order(-Post.created)
        self.render('page-blog-top.html', posts=posts)
