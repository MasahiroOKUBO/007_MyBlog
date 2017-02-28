from handlers import BaseHandler


class Logout(BaseHandler):
    """user can logout. redirect to /"""
    def get(self):
        self.logout()
        self.redirect('/')
        return
