from workflow import Workflow

from pocket_alfred import get_list


if __name__ == '__main__':
    wf = Workflow()
    print "Cache refreshed."
    wf.clear_cache()
    wf.cached_data('pocket_list', data_func=get_list, max_age=60)
