import webapp2

from handlers import TopPage
from handlers import Signup
from handlers import Welcome
from handlers import Login
from handlers import Logout
from handlers import BlogFront
from handlers import NewPost
from handlers import ShowPost
from handlers import EditPost
from handlers import DeletePost
from handlers import CastVote
from handlers import CastVeto
from handlers import NewComment
from handlers import ShowComment
from handlers import EditComment
from handlers import DeleteComment


app = webapp2.WSGIApplication([('/', TopPage),
                               ('/signup', Signup),
                               ('/welcome', Welcome),
                               ('/login', Login),
                               ('/logout', Logout),
                               ('/blog/?', BlogFront),
                               ('/blog/newpost', NewPost),
                               ('/blog/([0-9]+)/show', ShowPost),
                               ('/blog/([0-9]+)/edit', EditPost),
                               ('/blog/([0-9]+)/delete', DeletePost),
                               ('/blog/([0-9]+)/vote', CastVote),
                               ('/blog/([0-9]+)/veto', CastVeto),
                               ('/blog/([0-9]+)/comment/new', NewComment),
                               ('/blog/([0-9]+)/comment/([0-9]+)/show', ShowComment),
                               ('/blog/([0-9]+)/comment/([0-9]+)/edit', EditComment),
                               ('/blog/([0-9]+)/comment/([0-9]+)/delete', DeleteComment),
                               ],
                              debug=True)
