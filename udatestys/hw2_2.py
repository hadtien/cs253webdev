import webapp2
import cgi
import re

def escape_html(s):
    return cgi.escape(s, quote = True)

form = """
<h2>Signup</h2>
    <form method="post">
      <table>
        <tr>
          <td class="label">
            Username
          </td>
          <td>
            <input type="text" name="username" value="%(uname)s">
          </td>
          <td class="error">
            %(uname_error)s
          </td>
        </tr>

        <tr>
          <td class="label">
            Password
          </td>
          <td>
            <input type="password" name="password" value="">
          </td>
          <td class="error">
            %(pwd_error)s
          </td>
        </tr>

        <tr>
          <td class="label">
            Verify Password
          </td>
          <td>
            <input type="password" name="verify" value="">
          </td>
          <td class="error">
            %(pwd_error_match)s
          </td>
        </tr>

        <tr>
          <td class="label">
            Email (optional)
          </td>
          <td>
            <input type="text" name="email" value="%(email)s">
          </td>
          <td class="error">
            %(email_error)s
          </td>
        </tr>
      </table>

      <input type="submit">
    </form>"""


class MainPage(webapp2.RequestHandler):
    def write_form(self, uname="", uname_error="", pwd_error="", pwd_error_match="",
                   email="", email_error=""):
        self.response.out.write(form %{"uname": escape_html(uname),
                                       "email": escape_html(email),
                                       "uname_error": uname_error,
                                       "pwd_error": pwd_error,
                                       "pwd_error_match": pwd_error_match,
                                       "email_error": email_error})
    def get(self):
        self.write_form()

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')
        verify = self.request.get('verify')
        email = self.request.get('email')
        uname_error, pwd_error, pwd_error_match, email_error = '', '', '', ''

        print password, verify
        USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
        PWD_RE = re.compile(r"^.{3,20}$")
        EMAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")
        if not USER_RE.match(username):
            uname_error = "That's not a valid username."
        if not PWD_RE.match(password):
            pwd_error = "That wasn't a valid password."
        elif password != verify:
            pwd_error_match = "Your passwords didn't match."
        if email and not EMAIL_RE.match(email): #email optional
            email_error = "That's not a valid email."

        if uname_error or pwd_error or pwd_error_match or email_error:
            self.write_form(username, uname_error, pwd_error, pwd_error_match, email, email_error)
        else:
            self.redirect("/welcome?username=%s" % username)

class WelcomeHandler(webapp2.RequestHandler):
    def get(self):
        uname = self.request.get("username")
        self.response.out.write("Welcome, %s!" % uname)

application = webapp2.WSGIApplication([('/', MainPage),
                              ('/welcome', WelcomeHandler)],
                             debug=True)
