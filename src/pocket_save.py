import sys
import os
import urlparse
from pocket_api import Pocket, InvalidQueryException
from workflow import Workflow
import config


def main(wf):
    # Get tags
    tags = ["alfred"]
    if len(wf.args) and len(wf.args[0]):
        tags += [str(s.strip()) for s in wf.args[0].split(',')]

    current_app = os.popen("osascript -e 'application (path to frontmost "
                           "application as text)'").readline().rstrip()
    if current_app in ['Google Chrome', 'Safari']:
        if not add_item(get_browser_item(current_app), tags):
            print "%s link invalid." % current_app
            return 0
        print "%s link added to Pocket." % current_app
        wf.clear_cache()
        return 0
    else:
        item = get_clipboard_item()
        if item is not None:
            add_item(item, tags)
            print "Clipboard link added to Pocket."
            wf.clear_cache()
            return 0

    print "No link found!"
    return 0


def frontmost_app():
    return os.popen("osascript -e 'application (path to frontmost application"
                    "as text)'").readline().rstrip()


def get_browser_item(browser):
    url = title = None
    if browser == 'Google Chrome':
        url = os.popen("osascript -e 'tell application "
                       "\"/Applications/Google Chrome.app\" to return URL of "
                       "active tab of front window'").readline()
        title = os.popen("osascript -e 'tell application "
                         "\"/Applications/Google Chrome.app\" to return title "
                         "of active tab of front window'").readline()
    elif browser == 'Safari':
        url = os.popen("osascript -e 'tell application "
                       "\"/Applications/Safari.app\" to return URL of front "
                       "document'").readline()
        title = os.popen("osascript -e 'tell application "
                         "\"/Applications/Safari.app\" to return name of "
                         "front document'").readline()
    if url is None:
        return None
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


def add_item(item, tags):
    if item is not None:
        access_token = wf.get_password('pocket_access_token')
        pocket_instance = Pocket(config.CONSUMER_KEY, access_token)
        try:
            pocket_instance.add(
                url=item['url'], title=item['title'], tags=",".join(tags))
            return True
        except InvalidQueryException:
            pass
    return False


if __name__ == '__main__':
    wf = Workflow()
    sys.exit(wf.run(main))
