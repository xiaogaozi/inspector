# Inspector <https://github.com/xiaogaozi/inspector>
# Copyright (C) 2011  xiaogaozi <gaochangjian@gmail.com>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import urllib

import inspector.template
from inspector import datastore
from inspector import verify_user
from inspector.tasks import inspector_job
from inspector.inspectors import Inspectors

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp.util import login_required

class MainPage(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()
        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, {'user': user}))

class SignIn(webapp.RequestHandler):
    def get(self):
        self.redirect(users.create_login_url('/'))

class SignOut(webapp.RequestHandler):
    def get(self):
        self.redirect(users.create_logout_url('/'))

class About(webapp.RequestHandler):
    def get(self):
        self.response.out.write(inspector.template.render('about.html'))

class Submit(webapp.RequestHandler):
    @login_required
    def get(self):
        email = urllib.unquote(self.request.get('email'))
        if verify_user(email, self.response) == False:
            return

        template_values = {
            'email': email,
            'url': self.request.get('url'),
            'xpath': self.request.get('xpath')
        }
        for k, v in template_values.items():
            template_values[k] = urllib.quote(v)
        template_values['user'] = users.get_current_user()

        self.response.out.write(inspector.template.info('submit.html', template_values))

    def post(self):
        email = urllib.unquote(self.request.get('email'))
        if verify_user(email, self.response) == False:
            return

        url = urllib.unquote(self.request.get('url'))
        xpath = urllib.unquote(self.request.get('xpath'))
        status, html = inspector_job.get_html(url, xpath)
        if status == False:
            self.response.out.write(inspector.template.error(html))
            return

        rval = datastore.add_task(email, url, xpath, html)
        if rval == True:
            self.redirect('/')
        else:
            self.response.out.write(inspector.template.error(rval))

application = webapp.WSGIApplication([('/', MainPage),
                                      ('/signin', SignIn),
                                      ('/signout', SignOut),
                                      ('/submit', Submit),
                                      ('/about', About),
                                      ('/inspectors', Inspectors)],
                                     debug=False)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
