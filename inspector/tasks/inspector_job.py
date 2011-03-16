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
import cgi
import logging
import inspector.template
from inspector import datastore
from lib.BSXPath import BSXPathEvaluator, XPathResult

from google.appengine.api import mail
from google.appengine.api import urlfetch
from google.appengine.ext.webapp import template

def get_html(url, xpath=None):
    try:
        result = urlfetch.fetch(url)
    except urlfetch.DownloadError:
        logging.error('[DownloadError] ' + url)
        return False, "Can't fetch the contents of given URL. Try reload again, or check your network."
    except urlfetch.InvalidURLError:
        logging.error('[InvalidURLError] ' + url)
        return False, 'Invalid URL'

    if result.status_code != 200:
        logging.error('[HTTPError] "%s" %d' % (url, result.status_code))
        return False, 'HTTP Error: ' + result.status_code

    if xpath is None:
        return True, result.content
    else:
        document = BSXPathEvaluator(result.content)
        node = document.getFirstItem(xpath)
        if node is not None:
            return True, str(node)
        else:
            return False, 'XPath not found'

def check_update(url, xpath, oldhtml):
    status, newhtml = get_html(url, xpath)
    if status == False:
        return False, newhtml
    if newhtml != oldhtml.encode('utf-8'):
        return True, newhtml
    else:
        return False, None

def main():
    """Main progress."""
    message = mail.EmailMessage(sender="Inspector Notification <noreply@s~insp3cto2.appspotmail.com>",
                                subject="The page you inspected has been updated")
    for task in datastore.get_all():
        status, newhtml = check_update(task.url, task.xpath, task.html)
        if status == True:
            rval = datastore.update_task(task.key(), newhtml)
            if rval != True:
                logging.error(rval)
                continue
            message.to = task.email
            path = os.path.join(os.path.dirname(__file__), '../../webpages/notification_mail.html')
            message.html = template.render(path, {'html': cgi.escape(task.html.encode('utf-8')), 'url': task.url})
            message.send()

if __name__ == "__main__":
    main()
