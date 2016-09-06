import argparse
from workflow import Workflow


def main():
    wf = Workflow()

    args = parse_args(wf.args)

    title = 'Add this link'
    if args.add_archive:
        title = 'Add and archive this link'

    wf.add_item(title, arg=args.query, valid=True)

    tags = wf.cached_data('pocket_tags', max_age=0)
    if tags:
        for tag in tags:
            if args.query:
                autocomplete = '%s, #%s' % (args.query, tag)
            else:
                autocomplete = '#%s' % tag
            wf.add_item(' > Add #%s' % tag,
                        autocomplete=autocomplete,
                        valid=False)
    wf.send_feedback()


def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('--add-and-archive', dest='add_archive',
                        action='store_true', default=None)
    parser.add_argument('--add', dest='add',
                        action='store_true', default=None)
    parser.add_argument('query', nargs='?', default=None)
    return parser.parse_args(args)


if __name__ == '__main__':
    main()  # pragma: no cover
