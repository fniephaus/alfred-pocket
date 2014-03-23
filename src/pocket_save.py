import sys
import os
import urlparse
from pocket import Pocket
from workflow import Workflow

CONSUMER_KEY = '25349-924436f8cc1abc8370f02d9d'


def main(wf):
    if is_running('Google Chrome'):
        add_item(get_Chrome_item())
        print "Chrome link added to Pocket"
        wf.clear_cache()
        return 0
    elif is_running('Safari'):
        add_item(get_Safari_item())
        print "Safari link added to Pocket"
        wf.clear_cache()
        return 0
    else:
        item = get_clipboard_item()

        if item is not None:
            add_item(item)
            print "Clipboard link added to Pocket"
            wf.clear_cache()
            return 0

        print "No link found!"
        return 0


def is_running(app):
    return os.popen("""osascript -e 'tell app "System Events" to count processes whose name is "%s"' """ % app).read().rstrip() == "1"


def get_Chrome_item():
    url = os.popen(
        """ osascript -e 'tell application "Google Chrome" to return URL of active tab of front window' """).readline()
    title = os.popen(
        """ osascript -e 'tell application "Google Chrome" to return title of active tab of front window' """).readline()
    return {
        'url': url,
        'title': title
    }


def get_Safari_item():
    url = os.popen(
        """ osascript -e 'tell application "Safari" to return URL of front document' """).readline()
    title = os.popen(
        """ osascript -e 'tell application "Safari" to return name of front document' """).readline()
    return {
        'url': url,
        'title': title
    }


def get_clipboard_item():
    clipboard = os.popen(""" osascript -e "get the clipboard" """).readline()
    parts = urlparse.urlsplit(clipboard)
    if not parts.scheme or not parts.netloc:
        return None
    return {
        'url': clipboard,
        'title': None
    }


def add_item(item):
    access_token = wf.get_password('pocket_access_token')
    pocket_instance = Pocket(CONSUMER_KEY, access_token)
    pocket_instance.add(url=item['url'], title=item['title'], tags="alfred")


if __name__ == '__main__':
    wf = Workflow()
    sys.exit(wf.run(main))
