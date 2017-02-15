import os
import webapp2
import jinja2

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

class TopPage(BaseHandler):
  def get(self):
      self.render('page-top.html')


'''
 -----------------------
 Main
 -----------------------
'''
app = webapp2.WSGIApplication([('/', TopPage),
                               ],
                              debug=True)
