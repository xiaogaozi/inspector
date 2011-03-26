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

import re
import logging
import urllib
import urlparse

import inspector.template
from inspector.tasks import inspector_job

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

class Inspector(webapp.RequestHandler):
    def get(self):
        url = self.request.get('url')
        if url == '':
            self.response.out.write(inspector.template.error('URL required'))
            return

        o = urlparse.urlparse(url)
        if o.scheme == '':
            url = 'http://' + url

        status, html = inspector_job.get_html(url)
        if status == False:
            self.response.out.write(inspector.template.error(html))
        else:
            url = status
            self.response.out.write(self.process_html(html, url))

    def process_html(self, html, url):
        def create_tag(tagname, attrs, pair=True):
            tag = '<' + tagname
            for k, v in attrs.iteritems():
                tag += ' ' + k + '="' + v + '"'
            if pair:
                tag += '></' + tagname +'>'
            else:
                tag += ' />'
            return tag

        s = ''
        s += create_tag('script',
                        {'type': 'text/javascript',
                         'src': 'http://code.jquery.com/jquery-latest.min.js'})
        s += create_tag('script',
                        {'type': 'text/javascript',
                         'src': '/javascripts/inspector.min.js'})
        s += create_tag('input',
                        {'type': 'hidden',
                         'id': 'lan-email',
                         'value': urllib.quote(users.get_current_user().email())},
                        False)
        s += create_tag('input',
                        {'type': 'hidden',
                         'id': 'lan-request-url',
                         'value': urllib.quote(url)},
                        False)
        o = urlparse.urlparse(url)
        s += create_tag('input',
                        {'type': 'hidden',
                         'id': 'lan-url-host',
                         'value': urllib.quote(urlparse.urlunparse((o.scheme, o.netloc, '', '', '', '')))},
                        False)
        s += create_tag('input',
                        {'type': 'hidden',
                         'id': 'lan-url-path',
                         'value': urllib.quote(inspector_job.urlpath(url))},
                        False)

        try:
            charset = 'utf-8'
            m = re.search(r'(?i)charset=[\'"]?([^\'"]*)[\'"]?', html.decode(charset, 'ignore'))
            if m is not None:
                charset = m.groups()[0]
            if charset == 'gb2312' or charset == 'gbk':
                charset = 'gb18030'

            m = None
            m = re.search(r'(?i)(<body[^>]*>)', html.decode(charset))
            if m is not None:
                return re.sub(r'(?i)(<body[^>]*>)', r'\1' + s, html.decode(charset))
            m = None
            # FIXME: With frameset, the JS code won't be executed.
            m = re.search(r'(?i)(<frameset[^>]*>)', html.decode(charset))
            if m is not None:
                return re.sub(r'(?i)(<frameset[^>]*>)', r'\1' + s, html.decode(charset))
            return inspector.template.error("The page you request isn't standard.")
        except UnicodeDecodeError:
            logging.error('[UnicodeDecodeError] ' + url + ': ' + charset)
            return inspector.template.error('Unicode decode error')

application = webapp.WSGIApplication([('/inspect', Inspector)],
                                     debug=False)

def main():
    run_wsgi_app(application)
            
if __name__ == "__main__":
    main()
