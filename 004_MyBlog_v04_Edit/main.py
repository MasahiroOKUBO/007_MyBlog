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
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

'''
 -----------------------
 hash stuff
 -----------------------
'''
secret = 'fart'

def make_secure_val(val):
    return '%s|%s' % (val, hmac.new(secret, val).hexdigest())

def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val

def make_salt(length = 5):
    return ''.join(random.choice(letters) for x in xrange(length))

def make_pw_hash(name, pw, salt = None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s,%s' % (salt, h)

def valid_pw(name, password, h):
    salt = h.split(',')[0]
    return h == make_pw_hash(name, password, salt)

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

'''
 -----------------------
 data stuff
 -----------------------
'''
def users_key(namespace = 'default'):
    return ndb.Key('users', namespace)

class User(ndb.Model):
    name = ndb.StringProperty(required = True)
    pw_hash = ndb.StringProperty(required = True)
    email = ndb.StringProperty()

    @classmethod
    def by_id(cls, uid):
        return User.get_by_id(uid, parent = users_key())

    @classmethod
    def by_name(cls, name):
        u = User.query().filter(User.name == name).get()
        return u

    @classmethod
    def register(cls, name, pw, email = None):
        pw_hash = make_pw_hash(name, pw)
        return User(parent = users_key(),
                    name = name,
                    pw_hash = pw_hash,
                    email = email)

    @classmethod
    def login(cls, name, pw):
        u = cls.by_name(name)
        if u and valid_pw(name, pw, u.pw_hash):
            return u



def posts_key(namespace = 'default'):
    return ndb.Key('posts', namespace)

class Post(ndb.Model):
    subject = ndb.StringProperty(required = True)
    content = ndb.TextProperty(required = True)
    created = ndb.DateTimeProperty(auto_now_add = True)
    last_modified = ndb.DateTimeProperty(auto_now = True)
    author_key = ndb.KeyProperty(kind=User)

    def render(self):
        self._render_text = self.content.replace('\n', '<br>')
        post_id = str(self.key.id())
        author = self.author_key.get()
        print author
        return render_str("part-post.html",
                          p = self,
                          post_id=post_id)


'''
 -----------------------
 handler
 -----------------------
'''
class BaseHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        params['user'] = self.user
        return render_str(template, **params)

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
        self.user = uid and User.by_id(int(uid))

class TopPage(BaseHandler):
  def get(self):
      self.render('page-top.html')

class Signup(BaseHandler):
    def get(self):
        self.render("form-signup.html")

    def post(self):
        have_error = False
        self.username = self.request.get('username')
        self.password = self.request.get('password')
        self.verify = self.request.get('verify')
        self.email = self.request.get('email')

        params = dict(username = self.username,
                      email = self.email)

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
            self.render('signup-form.html', **params)
        else:
            self.done()

    def done(self, *a, **kw):
        #make sure the user doesn't already exist
        u = User.by_name(self.username)
        if u:
            msg = 'That user already exists.'
            self.render('form-signup.html', error_username = msg)
        else:
            u = User.register(self.username, self.password, self.email)
            u.put()

            self.login(u)
            self.redirect('/')

class Welcome(BaseHandler):
    def get(self):
        if self.user:
            self.render('page-welcome.html', username = self.user.name)
        else:
            self.redirect('/signup')

class Login(BaseHandler):
    def get(self):
        self.render('form-login.html')

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')

        u = User.login(username, password)
        if u:
            self.login(u)
            self.redirect('/')
        else:
            msg = 'Invalid login'
            self.render('form-login.html', error = msg)

class Logout(BaseHandler):
    def get(self):
        self.logout()
        self.redirect('/')

class BlogFront(BaseHandler):
    def get(self):
        # posts = Post.all().order('-created')
        posts = Post.query().order(-Post.created)
        self.render('page-blog-front.html', posts = posts)

class NewPost(BaseHandler):
    def get(self):
        if self.user:
            self.render("form-new-post.html")
        else:
            self.redirect("/login")

    def post(self):
        if not self.user:
            self.redirect('/blog')

        subject = self.request.get('subject')
        content = self.request.get('content')

        if subject and content:
            p = Post(parent = posts_key(), subject = subject, content = content)
            p.put()
            self.redirect('/blog/%s' % str(p.key.id()))
        else:
            error = "subject and content, please!"
            self.render("form-new-post.html", subject=subject, content=content, error=error)

class ShowPost(BaseHandler):
    def get(self, post_id):
        # post = Post.get_by_id(int(post_id)) # no work
        key = ndb.Key('Post', int(post_id), parent=posts_key())
        post = key.get()
        print post

        if not post:
            self.error(404)
            return
        self.render("page-blog-post.html", p=post)

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
            message="This is not your post!"
            self.render("page-message.html", message=message)
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
            self.render("page-message.html", message=message)
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
            self.render("page-message.html", message=message)
            return

        if post:
            post.key.delete()
            message="Delete succeeed!"
            self.render("page-message.html", message=message)
        else:
            error = "post does not exists!"
            self.render("page-message.html", message=error)


'''
 -----------------------
 main
 -----------------------
'''
app = webapp2.WSGIApplication([('/', TopPage),
                               ('/signup', Signup),
                               ('/welcome', Welcome),
                               ('/login', Login),
                               ('/logout', Logout),
                               ('/blog/?', BlogFront),
                               ('/blog/newpost', NewPost),
                               ('/blog/([0-9]+)', ShowPost),
                               ('/blog/([0-9]+)/edit', EditPost),
                               ('/blog/([0-9]+)/delete', DeletePost),
                               ],
                              debug=True)
