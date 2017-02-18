from google.appengine.ext import ndb
from models import User, Post


def comments_key(namespace='default'):
    return ndb.Key('comments', namespace)


class Comment(ndb.Model):
    subject = ndb.StringProperty(required=True)
    content = ndb.TextProperty(required=True)
    created = ndb.DateTimeProperty(auto_now_add=True)
    last_modified = ndb.DateTimeProperty(auto_now=True)
    author_key = ndb.KeyProperty(kind=User)
    post_key = ndb.KeyProperty(kind=Post)

    def render(self):
        self._render_text = self.content.replace('\n', '<br>')
        author_id = self.author_key.id()
        author = User.by_id(author_id)
        author_name = author.name
        post_id = self.post_key.id()
        comment_id = self.key.id()

        return render_str("part-comment.html",
                          c=self,
                          author=author_name,
                          post_id=post_id,
                          comment_id=comment_id)
