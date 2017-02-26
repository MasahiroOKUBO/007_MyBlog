from handlers import BaseHandler


class Logout(BaseHandler):
    def get(self):
        self.logout()
        self.redirect('/')
        return
