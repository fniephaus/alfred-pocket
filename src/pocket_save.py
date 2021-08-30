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
BROWSER_SCRIPTS = {
    'Firefox': {
        'url': """\
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
""",
        'title': """osascript -e 'tell application "Firefox" to return name of front window'"""
    },
    'Google Chrome': {
        'url': """osascript -e 'tell application "Google Chrome" to return URL of active tab of front window'""",
        'title': """osascript -e 'tell application "Google Chrome" to return title of active tab of front window'""",
    },
    'Google Chrome Canary': {
        'url': """osascript -e 'tell application "Google Chrome Canary" to return URL of active tab of front window'""",
        'title': """osascript -e 'tell application "Google Chrome Canary" to return title of active tab of front window'""",
    },
    'Chromium': {
        'url': """osascript -e 'tell application "Chromium" to return URL of active tab of front window'""",
        'title': """osascript -e 'tell application "Chromium" to return title of active tab of front window'""",
    },
    'Brave Browser': {
        'url': """osascript -e 'tell application "Brave Browser" to return URL of active tab of front window'""",
        'title': """osascript -e 'tell application "Brave Browser" to return title of active tab of front window'""",
    },
    'Vivaldi': {
        'url': """osascript -e 'tell application "Vivaldi" to return URL of active tab of front window'""",
        'title': """osascript -e 'tell application "Vivaldi" to return title of active tab of front window'""",
    },
    'Safari': {
        'url': """osascript -e 'tell application "Safari" to return URL of front document'""",
        'title': """osascript -e 'tell application "Safari" to return name of front document'""",
    },
    'Safari Technology Preview': {
        'url': """osascript -e 'tell application "Safari Technology Preview" to return URL of front document'""",
        'title': """osascript -e 'tell application "Safari Technology Preview" to return name of front document'""",
    },
    'Webkit': {
        'url': """osascript -e 'tell application "Webkit" to return URL of front document'""",
        'title': """osascript -e 'tell application "Webkit" to return name of front document'""",
    },
}


def main(_):
    args = parse_args(WF.args)

    if args.add_and_archive:
        add_method = add_and_archive_link
    else:
        add_method = add_link

    # Get tags
    tags = ['alfred']
    if args.tags:
        tags += [str(s.strip().strip('#').encode('utf-8')) for s in args.tags.split(',')]

    current_app = frontmost_app()
    link = get_browser_link(current_app)
    if link is not None:
        if not add_method(link, tags):
            print "%s link invalid." % current_app
            return
        print "%s link added to Pocket." % current_app
        WF.clear_cache()
        return

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
    scripts = BROWSER_SCRIPTS.get(browser)
    if scripts is None:
        return None
    url = os.popen(scripts['url']).readline()
    title = os.popen(scripts['title']).readline()
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
