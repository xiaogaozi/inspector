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

import urllib

import inspector.template
from inspector import datastore
from inspector import verify_user

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import login_required

class Inspectors(webapp.RequestHandler):
    @login_required
    def get(self):
        user = users.get_current_user()
        task_list = datastore.get_user_info(user.email())
        self.response.out.write(inspector.template.render('inspectors.html',
                                                          content_template_values={'task_list': task_list, 'page_str': 'page' if task_list.count() == 1 else 'pages', 'email': urllib.quote(user.email())}))

    def post(self):
        email = urllib.unquote(self.request.get('email'))
        if verify_user(email, self.response) == False:
            return

        keys = self.request.get_all('task_key')
        if len(keys) == 0:
            self.response.out.write(inspector.template.error('You should select at least one item.'))
            return

        if datastore.delete_tasks(keys) == True:
            self.redirect('/inspectors')
        else:
            self.response.out.write(inspector.template.error('Datastore delete error'))
