from google.appengine.ext import ndb
import models.User
import Vote
import jinja2
import os

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)


def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

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
