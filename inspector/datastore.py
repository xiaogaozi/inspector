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

from google.appengine.ext import db

class Task(db.Model):
    email = db.EmailProperty()
    url = db.LinkProperty()
    xpath = db.StringProperty()
    html = db.TextProperty()

def add_task(email, url, xpath, html):
    e = db.Email(email)
    u = db.Link(url)
    if isduplicated(e, u, xpath) == False:
        task = Task(email=e, url=u, xpath=xpath, html=_set_task_html(html))
        try:
            task.put()
            return True
        except db.Error:
            return 'Datastore save error'
    else:
        return "You have inspected this portion."

def update_task(key, newhtml):
    task = db.get(key)
    try:
        task.html = _set_task_html(newhtml)
        try:
            task.put()
            return True
        except db.Error:
            return '[DBError] Datastore update error'
    except UnicodeDecodeError:
        return '[UnicodeDecodeError] ' + task.url

def isduplicated(email, url, xpath):
    query = db.GqlQuery("SELECT * FROM Task "
                        "WHERE email = :email "
                        "AND url = :url "
                        "AND xpath = :xpath",
                        email=email, url=url, xpath=xpath)
    if query.count() == 0:
        return False
    else:
        return True

def get_user_info(email):
    query = db.GqlQuery("SELECT * FROM Task "
                        "WHERE email = :1", email)
    return query

def get_task_html(key):
    task = db.get(key)
    return task.html.encode('utf-8')

def get_all():
    return Task.all()

def delete_tasks(keys):
    try:
        for key in keys:
            db.delete(key)
        return True
    except db.Error:
        return False

def _set_task_html(html):
    return html.decode('utf-8')
