from google.appengine.ext import ndb
from models import User, Vote

def posts_key(namespace='default'):
    return ndb.Key('posts', namespace)


class Post(ndb.Model):
    subject = ndb.StringProperty(required=True)
    content = ndb.TextProperty(required=True)
    created = ndb.DateTimeProperty(auto_now_add=True)
    last_modified = ndb.DateTimeProperty(auto_now=True)
    author_key = ndb.KeyProperty(kind=User)

    def render(self):
        self._render_text = self.content.replace('\n', '<br>')
        post_id = str(self.key.id())
        author_id = self.author_key.id()
        author = User.by_id(author_id)
        author_name = author.name
        votes = Vote.query().filter(Vote.post_key == self.key).count()
        return render_str("part-post.html",
                          p=self,
                          post_id=post_id,
                          author=author_name,
                          likes=votes)
