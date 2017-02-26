from handlers import BaseHandler


class TopPage(BaseHandler):
    def get(self):
        self.render('page-top.html')
        return
