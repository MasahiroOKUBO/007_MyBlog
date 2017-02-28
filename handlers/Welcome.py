from handlers import BaseHandler


class Welcome(BaseHandler):
    """Welcome page for Signup user."""
    def get(self):
        if self.user:
            self.render('page-welcome.html', username=self.user.name)
            return
        else:
            self.redirect('/signup')
            return
