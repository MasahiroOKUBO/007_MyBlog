from handlers import BaseHandler
from models import User

class Login(BaseHandler):
    def get(self):
        self.render('form-login.html')
        return

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')

        u = User.login(username, password)
        if u:
            self.login(u)
            self.redirect('/')
            return
        else:
            msg = 'Invalid login'
            self.render('form-login.html', error=msg)
            return
