import os
import webapp2
import re
import jinja2
from google.appengine.ext import db
import hmac

SECRET = "mumbojumbohenrymarsau"
template_dir = os.path.join(os.path.dirname(__file__), '.')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=True)


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))


class SignupPage(Handler):
    def get(self):
        self.render("signup.htm")

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')
        verify = self.request.get('verify')
        email = self.request.get('email')
        uname_error, pwd_error, pwd_error_match, email_error, uname_exists = '', '', '', '', ''

        user_re = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
        pwd_re = re.compile(r"^.{3,20}$")
        email_re = re.compile(r"^[\S]+@[\S]+\.[\S]+$")
        if not user_re.match(username):
            uname_error = "That's not a valid username."
        if not pwd_re.match(password):
            pwd_error = "That wasn't a valid password."
        elif password != verify:
            pwd_error_match = "Your passwords didn't match."
        if email and not email_re.match(email): #email optional
            email_error = "That's not a valid email."

        user = User(username=username, password_hash=User.create_pwd_hash(password=password))

        q = User.all()
        q.filter("username =", username)

        if q.count() > 0:
            uname_exists = "Username exists"
        if uname_error or pwd_error or pwd_error_match or email_error or uname_exists:
            self.render("signup.htm", username_error=uname_error, password_error=pwd_error,
                        verify_error=pwd_error_match, email_error=email_error, usernam=username,
                        email=email, username_exists=uname_exists)
        else:
            user.put()
            self.response.headers.add_header('Set-Cookie', 'uname=%s;Path=/' % str(username))
            self.redirect("/welcome")


class WelcomeHandler(webapp2.RequestHandler):
    def get(self):
        uname = self.request.cookies.get("uname")
        self.response.out.write("Welcome, %s!" % uname)


class Entry(db.Model):
    title = db.StringProperty(required=True)
    body = db.TextProperty(required=True)
    created = db.DateProperty(auto_now_add=True)


class User(db.Model):
    username = db.StringProperty(required=True)
    password_hash = db.StringProperty(required=True)

    @staticmethod
    def create_pwd_hash(password):
        return hmac.new(SECRET, password).hexdigest()

    @staticmethod
    def validate_pwd(password, h):
        return hmac.new(SECRET, password).hexdigest() == h


class MainPage(Handler):
    def render_front(self):
        entries = db.GqlQuery("SELECT * FROM Entry ORDER BY created DESC")
        self.render("front.html", entries=entries)

    def get(self):
        self.render_front()


class LoginPage(Handler):
    def get(self):
        self.render("login.htm")

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')

        q = User.all()
        q.filter("username =", username)
        if q.count() == 0:  # user doesn't exist
            self.render("login.htm", invalid_login="User doesn't exist")
            return
        user = q.get()
        if not User.validate_pwd(password, user.password_hash):
            self.render("login.htm", invalid_login="Wrong password")
            return
        else:
            self.redirect("/welcome?username=%s" % username)
            self.response.headers.add_header('Set-Cookie', 'uname=%s;Path=/' % str(username))
            self.redirect("/welcome")

class LogoutPage(Handler):
    def get(self):
        self.response.headers.add_header('Set-Cookie', 'uname=;Path=/')
        self.redirect("/signup")

class NewPost(Handler):
    def get(self):
        self.render("new_entry.html")

    def post(self):
        title = self.request.get("subject")
        body = self.request.get("content")
        if title and body:
            a = Entry(title=title, body=body)
            a.put()
            self.redirect("/%s" % str(a.key().id()))
        else:
            error = "we need both a title and a body!"
            self.render("new_entry.html", title=title, body=body, error=error)

class PostPage(Handler):
    def get(self, post_id):
        post = Entry.get_by_id(int(post_id), None)
        self.write('<h1>' + post.title + '</h1><br>' + post.body + '<br><a href="..">Main</a>')


application = webapp2.WSGIApplication([('/', MainPage),
                                       ('/welcome', WelcomeHandler),
                                       ('/signup', SignupPage),
                                       ('/newpost', NewPost),
                                       ('/login', LoginPage),
                                       ('/(\d+)', PostPage),
                                       ('/logout', LogoutPage)],
                                      debug=True)
