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

from google.appengine.api import users
from google.appengine.ext.webapp import template

PAGE_BASE_PATH = '../webpages/'
HEADER_PATH = os.path.join(os.path.dirname(__file__), os.path.join(PAGE_BASE_PATH, 'header.html'))
TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), os.path.join(PAGE_BASE_PATH, 'template.html'))

def render(content_file, icontype=None, content_template_values={}):
    """A render specifically for Inspector project. """
    template_values = {}

    # Header
    header_path = os.path.join(os.path.dirname(__file__), HEADER_PATH)
    user = users.get_current_user()
    template_values['header'] = template.render(header_path, {'user': user})

    # Content
    content_path = os.path.join(os.path.dirname(__file__), os.path.join(PAGE_BASE_PATH, content_file))
    template_values['content'] = template.render(content_path, content_template_values)

    # Icon type
    if icontype is not None:
        template_values['icontype'] = icontype

    template_path = os.path.join(os.path.dirname(__file__), TEMPLATE_PATH)
    return template.render(template_path, template_values)

def error(error_message):
    return render('error.html', 'error', {'message': error_message})

def info(content_file, content_template_values={}):
    return render(content_file, 'info', content_template_values)
