import webapp2
import cgi

def escape_html(s):
    return cgi.escape(s, quote = True)

form = """
<h2>Enter some text to ROT13:</h2>
    <form method="post">
      <textarea name="text"
                style="height: 100px; width: 400px;">%(text)s</textarea>
      <br>
      <input type="submit">
    </form>
"""

def rot13(text):
    res = ''
    for ch in text:
        if ch in 'abcdefghijklmABCDEFGHIJKLM':
            res += chr(ord(ch) + 13)
        elif ch in 'nopqrstuvwxyzNOPQRSTUVWXYZ':
            res += chr(ord(ch) - 13)
        else: res += ch
    return res

class MainPage(webapp2.RequestHandler):
    def write_form(self, text=""):
        self.response.out.write(form % {'text':escape_html(text)})

    def get(self):
        self.write_form()

    def post(self):
        user_text = self.request.get('text')
        self.write_form(rot13(user_text))




application = webapp2.WSGIApplication([('/', MainPage)], debug=True)