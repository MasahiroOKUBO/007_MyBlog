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
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

def jinja_render_template(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

'''
 -----------------------
 hash stuff
 -----------------------
'''
salt_cookie = '27!#gserug'

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
        user = User(parent = users_key(),
                    name = name,
                    pw_hash = pw_hash,
                    email = email)
        return user

    @classmethod
    def login(cls, name, pw):
        user = cls.get_user_by_name(name)
        if user and valid_pw(name, pw, user.pw_hash):
            return user

'''
 -----------------------
 handler
 -----------------------
'''
class BaseHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        return jinja_render_template(template, **params)

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
        user = User.get_user_by_name(self.username)
        if user:
            msg = 'That user already exists.'
            self.render('form-signup.html', error_username=msg)
        else:
            user = User.register(self.username, self.password, self.email)
            user.put()
            self.login(user)
            self.redirect('/welcome')

class Welcome(BaseHandler):
    def get(self):
        if self.user:
            self.render('page-welcome.html', username=self.user.name)
        else:
            self.redirect('/signup')

'''
 -----------------------
 Main
 -----------------------
'''
app = webapp2.WSGIApplication([('/', TopPage),
                               ('/signup', Signup),
                               ('/welcome', Welcome),
                               ],
                              debug=True)
