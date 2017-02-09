import os
import re
import random
import hashlib
import hmac
from string import letters

import webapp2
import jinja2

from google.appengine.ext import ndb

'''
 -----------------------
 jinja stuff
 -----------------------
'''
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=True)
def jinja_render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

'''
 -----------------------
 hash stuff
 -----------------------
'''
salt_cookie = 'fart'

def make_secure_val(val):
    return '%s|%s' % (val, hmac.new(salt_cookie, val).hexdigest())

def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val

def make_random_salt(length=5):
    return ''.join(random.choice(letters) for x in xrange(length))

def make_pw_hash(name, pw, salt=None):
    if not salt:
        salt = make_random_salt()
    hash = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s,%s' % (salt, hash)

def valid_pw(name, password, hash):
    salt = hash.split(',')[0]
    return hash == make_pw_hash(name, password, salt)

'''
 -----------------------
 data stuff
 -----------------------
'''
def users_key(namespace = 'default'):
    return ndb.Key('users', namespace)

def posts_key(namespace ='default'):
    return ndb.Key('blogs', namespace)

def votes_key(namespace ='default'):
    return ndb.Key('votes', namespace)

def comments_key(namespace ='default'):
    return ndb.Key('comments', namespace)

class User(ndb.Model):
    name = ndb.StringProperty(required = True)
    pw_hash = ndb.StringProperty(required = True)
    email = ndb.StringProperty()

    @classmethod
    def get_user_by_id(cls, ID):
        user = User.get_by_id(ID, parent = users_key())
        return user

    @classmethod
    def get_user_by_name(cls, name):
        user = User.query().filter(User.name == name).get()
        return user

    @classmethod
    def register(cls, name, pw, email = None):
        pw_hash = make_pw_hash(name, pw)
        return User(parent = users_key(),
                    name = name,
                    pw_hash = pw_hash,
                    email = email)

    @classmethod
    def login(cls, name, pw):
        user = cls.get_user_by_name(name)
        if user and valid_pw(name, pw, user.pw_hash):
            return user

class Post(ndb.Model):
    subject = ndb.StringProperty(required=True)
    content = ndb.TextProperty(required=True)
    created = ndb.DateTimeProperty(auto_now_add=True)
    last_modified = ndb.DateTimeProperty(auto_now=True)
    author_key = ndb.KeyProperty(kind=User)

    def render(self):
        self._render_text = self.content.replace('\n', '<br>')
        ID = str(self.key.id())
        author_id=self.author_key.id()
        author = User.get_user_by_id(author_id)
        author_name=author.name
        return jinja_render_str("post.html", p=self, id=ID, author=author_name)

class Vote(ndb.Model):
    voter_key = ndb.KeyProperty(kind=User)
    post_key = ndb.KeyProperty(kind=Post)

class Comment(ndb.Model):
    content = ndb.TextProperty(required=True)
    created = ndb.DateTimeProperty(auto_now_add=True)
    last_modified = ndb.DateTimeProperty(auto_now=True)
    author_key = ndb.KeyProperty(kind=User)

    def render(self):
        self._render_text = self.content.replace('\n', '<br>')
        author_id=self.author_key.id()
        author = User.get_user_by_id(author_id)
        author_name=author.name
        return jinja_render_str("comment.html", comment=self, author=author_name)


'''
 -----------------------
 handler
 -----------------------
'''
class BlogHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        params['user'] = self.user
        return jinja_render_str(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def set_secure_cookie(self, name, val):
        cookie_val = make_secure_val(val)
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; Path=/' % (name, cookie_val))

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)

    def login(self, user):
        self.set_secure_cookie('user_id', str(user.key.id()))

    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.get_user_by_id(int(uid))

class MainPage(BlogHandler):
  def get(self):
      self.render('page-top.html')

class Login(BlogHandler):
    def get(self):
        redirect_url = self.request.get("redirectUrl")
        if not redirect_url:
            redirect_url = '/welcome'
        self.render('form-login.html', redirectUrl=redirect_url)

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')
        redirect_url = self.request.get("redirectUrl")
        print redirect_url
        u = User.login(username, password)
        if u:
            self.login(u)
            self.redirect(redirect_url)
        else:
            msg = 'Invalid login'
            self.render('form-login.html', error=msg)

class Logout(BlogHandler):
    def get(self):
        self.logout()
        self.redirect('/')

class Signup(BlogHandler):
    def get(self):
        self.render("form-signup.html")

    def post(self):
        have_error = False
        self.username = self.request.get('username')
        self.password = self.request.get('password')
        self.verify = self.request.get('verify')
        self.email = self.request.get('email')

        params = dict(username=self.username,
                      email=self.email)

        if not valid_username(self.username):
            params['error_username'] = "That's not a valid username."
            have_error = True

        if not valid_password(self.password):
            params['error_password'] = "That wasn't a valid password."
            have_error = True
        elif self.password != self.verify:
            params['error_verify'] = "Your passwords didn't match."
            have_error = True

        if not valid_email(self.email):
            params['error_email'] = "That's not a valid email."
            have_error = True

        if have_error:
            self.render('form-signup.html', **params)
        else:
            self.done()

    def done(self, *a, **kw):
        # make sure the user doesn't already exist
        u = User.get_user_by_name(self.username)
        if u:
            msg = 'That user already exists.'
            self.render('form-signup.html', error_username=msg)
        else:
            u = User.register(self.username, self.password, self.email)
            u.put()

            self.login(u)
            self.redirect('/welcome')

class Welcome(BlogHandler):
    def get(self):
        if self.user:
            self.render('page-welcome.html', username=self.user.name)
        else:
            self.redirect('/signup')

class BlogFront(BlogHandler):
    def get(self):
        posts = Post.query()
        posts = posts.order(-Post.created)
        self.render('page-blogfront.html', posts=posts)

class NewPost(BlogHandler):
    def get(self):
        if self.user:
            self.render("form-newpost.html")
        else:
            self.redirect("/login?redirectUrl=/blog/newpost")

    def post(self):
        if not self.user:
            self.redirect('/blog')

        subject = self.request.get('subject')
        content = self.request.get('content')
        author_key = self.user.key

        if subject and content:
            p = Post(parent=posts_key(), subject=subject, content=content, author_key=author_key)
            p.put()
            self.redirect('/blog/%s' % str(p.key.id()))
        else:
            error = "subject and content, please!"
            self.render("form-newpost.html", subject=subject, content=content, error=error)

class ShowPost(BlogHandler):
    def get(self, post_id):
        key = ndb.Key('Post', int(post_id), parent=posts_key())
        post = key.get()

        if not post:
            self.error(404)
            return

        plus_one_link = '/blog/%s/plus1' % str(post.key.id())
        minus_one_link = '/blog/%s/minus1' % str(post.key.id())

        self.render("page-showpost.html",
                    post=post,
                    plus_one_link=plus_one_link,
                    minus_one_link=minus_one_link,)

class EditPost(BlogHandler):
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
            message="This is not your post!"
            self.render("page-deleteconfirm.html", message=message)
            return

        self.render("form-editpost.html", post=post)

    def post(self, post_id):
        if not self.user:
            self.redirect('/login')
            return
        post_key = ndb.Key('Post', int(post_id), parent=posts_key())
        post = post_key.get()
        author_id = post.author_key.id()
        login_id = self.user.key.id()
        if not author_id == login_id:
            message="This is not your post!"
            self.render("page-deleteconfirm.html", message=message)
            return
        key = ndb.Key('Post', int(post_id), parent=posts_key())
        post = key.get()
        post.subject = self.request.get('subject')
        post.content = self.request.get('content')

        if post.subject and post.content:
            post.put()
            self.redirect('/blog/%s' % str(post.key.id()))
        else:
            error = "subject and content, please!"
            self.render("form-editpost.html", subject=subject, content=content, error=error)

class DeletePost(BlogHandler):
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
            message="This is not your post!"
            self.render("page-deleteconfirm.html", message=message)
            return

        self.render("form-deletepost.html", post=post)

    def post(self, post_id):
        if not self.user:
            self.redirect('/login')
            return

        key = ndb.Key('Post', int(post_id), parent=posts_key())
        post = key.get()

        author_id = post.author_key.id()
        login_id = self.user.key.id()
        if not author_id == login_id:
            message="This is not your post!"
            self.render("page-deleteconfirm.html", message=message)
            return

        if post:
            post.key.delete()
            message="Delete succeeed!"
            self.render("page-deleteconfirm.html", message=message)
        else:
            error = "post does not exists!"
            self.render("page-deleteconfirm.html", message=error)

class PlusOne(BlogHandler):
    def get(self, post_id):
        if not self.user:
            self.redirect('/login')
            return
        post_key = ndb.Key('Post', int(post_id), parent=posts_key())
        post = post_key.get()
        if not post:
            self.error(404)
            return

        author_id = post.author_key.id()
        login_id = self.user.key.id()
        if author_id == login_id:
            message="do not Plus 1 your self !"
            self.render("page-deleteconfirm.html", message=message)
            return

        self.render("form-plusminus.html", post=post)

    def post(self, post_id):
        if not self.user:
            self.redirect('/login')
            return

        key = ndb.Key('Post', int(post_id), parent=posts_key())
        post = key.get()
        voter_key = self.user.key

        if voter_key and post.key:
            vote = Vote(parent=votes_key(), voter_key=voter_key, post_key=post.key)
            vote.put()
            message = "vote suceeded!"
            self.render("page-deleteconfirm.html", message=message)
        else:
            error = "voter_key and post_key, needed!"
            self.render("page-deleteconfirm.html", message=error)

class MinusOne(BlogHandler):
    def get(self, post_id):
        if not self.user:
            self.redirect('/login')
            return
        post_key = ndb.Key('Post', int(post_id), parent=posts_key())
        post = post_key.get()
        author_id = post.author_key.id()
        login_id = self.user.key.id()
        if author_id == login_id:
            message="do not Plus 1 your self !"
            self.render("page-deleteconfirm.html", message=message)
            return

        voter_key = self.user.key

        if voter_key and post_key:
            vote = Vote(parent=votes_key(), voter_key=voter_key, post_key=post.key)
            vote.put()
            message = "vote suceeded!"
            self.render("page-deleteconfirm.html", message=message)
        else:
            error = "voter_key and post_key, needed!"
            self.render("page-deleteconfirm.html", message=error)


'''
 -----------------------
 sanity check
 -----------------------
'''
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASS_RE = re.compile(r"^.{3,20}$")
EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')

def valid_username(username):
    return username and USER_RE.match(username)

def valid_password(password):
    return password and PASS_RE.match(password)

def valid_email(email):
    return not email or EMAIL_RE.match(email)

def render_post(response, post):
  response.out.write('<b>' + post.subject + '</b><br>')
  response.out.write(post.content)

'''
 -----------------------
 Main
 -----------------------
'''
app = webapp2.WSGIApplication([('/', MainPage),
                               ('/login', Login),
                               ('/logout', Logout),
                               ('/signup', Signup),
                               ('/welcome', Welcome),
                               ('/blog/?', BlogFront),
                               ('/blog/newpost', NewPost),
                               ('/blog/([0-9]+)', ShowPost),
                               ('/blog/([0-9]+)/edit', EditPost),
                               ('/blog/([0-9]+)/delete', DeletePost),
                               ('/blog/([0-9]+)/plus1', PlusOne),
                               ('/blog/([0-9]+)/minus1', MinusOne),
                               ],
                              debug=True)
