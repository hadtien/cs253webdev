import os
import webapp2
import jinja2
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), '.')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)
    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Entry(db.Model):
    title = db.StringProperty(required = True)
    body = db.TextProperty(required = True)
    created = db.DateProperty(auto_now_add = True)

class MainPage(Handler):
    def render_front(self):
        entries = db.GqlQuery("SELECT * FROM Entry ORDER BY created DESC")
        self.render("front.html",  entries = entries)
    def get(self):
        self.render_front()

class NewPost(Handler):
    def get(self):
        self.render("new_entry.html")
    def post(self):
        title = self.request.get("subject")
        body = self.request.get("content")
        if title and body:
            a = Entry(title = title, body = body)
            a.put()
            self.redirect("/%s" % str(a.key().id()))
        else:
            error = "we need both a title and a body!"
            self.render("new_entry.html", title = title, body = body, error = error)

class PostPage(Handler):
    def get(self, id):
        post = Entry.get_by_id (int(id), None)
        self.write('<h1>' + post.title + '</h1><br>' + post.body + '<br><a href="..">Main</a>')


#e1, e2 = Entry(title="test", body="hello world!"), Entry(title="four tet", body="is great!")
#e1.put()
#e2.put()
application = webapp2.WSGIApplication([('/', MainPage),
                                       ('/newpost', NewPost),
                                       ('/(\d+)', PostPage)], debug=True)
