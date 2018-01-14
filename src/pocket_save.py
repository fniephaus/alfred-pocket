import argparse
import os
import subprocess
import urlparse
from pocket_api import Pocket, InvalidQueryException
from workflow import Workflow
import config

WF = Workflow()
POCKET = Pocket(config.CONSUMER_KEY, WF.get_password('pocket_access_token'))

FRONTMOST_APP = """\
osascript -e 'application (path to frontmost application as text)'\
"""
CHROME_URL = """\
osascript -e 'tell application "Google Chrome" to return URL of active tab of \
front window'\
"""
CHROME_TITLE = """\
osascript -e 'tell application "Google Chrome" to return title of active tab \
of front window'\
"""
SAFARI_URL = """\
osascript -e 'tell application "Safari.app" to return URL of front document'\
"""
SAFARI_TITLE = """\
osascript -e 'tell application "Safari.app" to return name of front document'\
"""

FIREFOX_URL = """\
osascript -e 'tell application "Firefox" to activate\n \
  set old_clipboard to the clipboard\n \
  tell application "System Events"\n \
      repeat until (exists window 1 of process "Firefox") \n \
        delay 0.1 \n \
      end repeat\n \
      keystroke "l" using command down\n \
      keystroke "c" using command down\n \
  end tell\n \
  delay .5\n \
  set new_clipboard to the clipboard\n \
  set the clipboard to old_clipboard\n \
  return new_clipboard' \
"""

FIREFOX_TITLE = """\
osascript -e 'tell application "Firefox" to return name of front window'\
"""


def main(_):
    args = parse_args(WF.args)

    if args.add_and_archive:
        add_method = add_and_archive_link
    else:
        add_method = add_link

    # Get tags
    tags = ['alfred']
    if args.tags:
        tags += [str(s.strip().strip('#')) for s in args.tags.split(',')]

    current_app = frontmost_app()
    if current_app in ['Google Chrome', 'Safari', 'Firefox']:
        link = get_browser_link(current_app)
        if not add_method(link, tags):
            print "%s link invalid." % current_app
            return
        print "%s link added to Pocket." % current_app
        WF.clear_cache()
        return
    else:
        link = get_link_from_clipboard()
        if link is not None:
            add_method(link, tags)
            print 'Clipboard link added to Pocket.'
            WF.clear_cache()
            return

    print 'No link found!'


def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('--add-and-archive', dest='add_and_archive',
                        action='store_true', default=None)
    parser.add_argument('tags', nargs='?', default=None)
    return parser.parse_args(args)


def frontmost_app():
    return os.popen(FRONTMOST_APP).readline().rstrip()


def get_browser_link(browser):
    url = title = url_script = title_script = None
    if browser == 'Google Chrome':
        url_script = CHROME_URL
        title_script = CHROME_TITLE
    elif browser == 'Safari':
        url_script = SAFARI_URL
        title_script = SAFARI_TITLE
    elif browser == 'Firefox':
        url_script = FIREFOX_URL
        title_script = FIREFOX_TITLE

    url = os.popen(url_script).readline()
    title = os.popen(title_script).readline()

    if url is None or title is None:
        return None
    return {
        'url': url.strip('\n'),
        'title': title.strip('\n')
    }


def get_link_from_clipboard():
    p = subprocess.Popen(['pbpaste', 'r'],
                         stdout=subprocess.PIPE, close_fds=True)
    clipboard, stderr = p.communicate()
    if stderr:
        return None
    parts = urlparse.urlsplit(clipboard)
    if not parts.scheme or not parts.netloc:
        return None
    return {
        'url': clipboard,
        'title': None
    }


def add_link(item, tags):
    if item:
        try:
            return POCKET.add(url=item['url'], title=item['title'],
                              tags=','.join(tags))[0]
        except InvalidQueryException:
            pass
    return None


def add_and_archive_link(link, tags):
    result = add_link(link, tags)
    if (not result or 'status' not in result or 'item' not in result or
            'item_id' not in result['item']):
        WF.logger.debug(result)
        return False

    POCKET.archive(result['item']['item_id'], wait=False)
    return True


if __name__ == '__main__':
    WF.run(main)
