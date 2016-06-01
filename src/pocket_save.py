import argparse
import os
import urlparse
from pocket_api import Pocket, InvalidQueryException
from workflow import Workflow
import config

WF = Workflow()
POCKET = Pocket(config.CONSUMER_KEY, WF.get_password('pocket_access_token'))


def main(_):
    args = parse_args(WF.args)

    if args.add_and_archive:
        add_method = add_and_archive_link
    else:
        add_method = add_link

    # Get tags
    tags = ["alfred"]
    if args.tags:
        tags += [str(s.strip()) for s in args.tags.split(',')]

    current_app = frontmost_app()
    if current_app in ['Google Chrome', 'Safari']:
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
            print "Clipboard link added to Pocket."
            WF.clear_cache()
            return

    print "No link found!"


def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('--add-and-archive', dest='add_and_archive',
                        action='store_true', default=None)
    parser.add_argument('tags', nargs='?', default=None)
    return parser.parse_args(args)


def frontmost_app():
    return os.popen("osascript -e 'application (path to frontmost application "
                    "as text)'").readline().rstrip()


def get_browser_link(browser):
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
        'url': url.strip('\n'),
        'title': title
    }


def get_link_from_clipboard():
    clipboard = os.popen(""" osascript -e "get the clipboard" """).readline()
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
                              tags=",".join(tags))[0]
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
