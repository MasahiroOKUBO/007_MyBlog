from google.appengine.ext import ndb
import jinja2
import os

from User import User, users_key

template_dir = os.path.join(os.path.dirname(__file__), '../templates')
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


    def render(post):
        post._render_text = post.content.replace('\n', '<br>')
        post_id = str(post.key.id())
        author_id = post.author_key.id()
        author = User.by_id(author_id)
        author_name = author.name
        votes = Vote.query().filter(Vote.post_key == post.key).count()
        created = post.created.strftime("%b %d, %Y")
        subject = post.subject
        return render_str("part-post.html",
                          # p=Post,
                          post_id=post_id,
                          subject=subject,
                          author=author_name,
                          likes=votes,
                          created=created,
                          render_content=post._render_text)


def votes_key(namespace='default'):
    return ndb.Key('votes', namespace)


class Vote(ndb.Model):
    voter_key = ndb.KeyProperty(kind=User)
    post_key = ndb.KeyProperty(kind=Post)


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
