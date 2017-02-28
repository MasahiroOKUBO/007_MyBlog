from handlers import BaseHandler


class TopPage(BaseHandler):
    """Service Top page"""
    def get(self):
        self.render('page-top.html')
        return
