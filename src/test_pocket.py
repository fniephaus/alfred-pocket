import unittest
import logging
import sys

import pocket
import pocket as pocket_backup

import test_data

CachedData = {}
Passwords = {}


class PocketTestCase(unittest.TestCase):

    def test_main_initial(self):
        pocket.WF._version.major = 'x'  # make sure that WF.first_run is True
        CachedData['__workflow_update_status'] = {
            'available': True
        }
        CachedData['pocket_tags'] = ['tag1']
        sys.argv = ['pocket.py', '']

        def send_feedback():
            pass
        pocket.WF.send_feedback = send_feedback
        pocket.WF._items = []
        pocket.main(None)
        # Update available item + categories
        self.assertEquals(len(pocket.WF._items), 1 + len(pocket.CATEGORIES))

    def test_main_search_all(self):
        CachedData['__workflow_update_status'] = {
            'available': False
        }
        CachedData['pocket_list'] = test_data.get_normal()
        sys.argv = ['pocket.py', 'e.com']

        def send_feedback():
            pass
        pocket.WF.send_feedback = send_feedback
        pocket.WF._items = []
        pocket.main(None)
        self.assertEquals(len(pocket.WF._items), 2)

    def test_main_mylist(self):
        CachedData['__workflow_update_status'] = {
            'available': False
        }
        CachedData['pocket_list'] = test_data.get_normal()
        sys.argv = ['pocket.py', 'in:mylist ']

        def send_feedback():
            pass
        pocket.WF.send_feedback = send_feedback
        pocket.WF._items = []
        pocket.main(None)
        self.assertEquals(len(pocket.WF._items), 3)

    def test_main_archive(self):
        CachedData['__workflow_update_status'] = {
            'available': False
        }
        CachedData['pocket_list'] = test_data.get_normal()
        sys.argv = ['pocket.py', 'in:archive ']

        def send_feedback():
            pass
        pocket.WF.send_feedback = send_feedback
        pocket.WF._items = []
        pocket.main(None)
        self.assertTrue(len(pocket.WF._items), 1)
        self.assertTrue('archive.com' in pocket.WF._items[0].subtitle)

    def test_main_favorite(self):
        CachedData['__workflow_update_status'] = {
            'available': False
        }
        CachedData['pocket_list'] = test_data.get_normal()
        sys.argv = ['pocket.py', 'in:favorites ']

        def send_feedback():
            pass
        pocket.WF.send_feedback = send_feedback
        pocket.WF._items = []
        pocket.main(None)
        self.assertTrue(len(pocket.WF._items), 1)
        self.assertTrue('fniephaus.com' in pocket.WF._items[0].subtitle)

    def test_main_articles(self):
        CachedData['__workflow_update_status'] = {
            'available': False
        }
        CachedData['pocket_list'] = test_data.get_normal()
        sys.argv = ['pocket.py', 'in:articles ']

        def send_feedback():
            pass
        pocket.WF.send_feedback = send_feedback
        pocket.WF._items = []
        pocket.main(None)
        self.assertTrue(len(pocket.WF._items), 1)
        self.assertTrue('google.com' in pocket.WF._items[0].subtitle)

    def test_main_videos(self):
        CachedData['__workflow_update_status'] = {
            'available': False
        }
        CachedData['pocket_list'] = test_data.get_normal()
        sys.argv = ['pocket.py', 'in:videos ']

        def send_feedback():
            pass
        pocket.WF.send_feedback = send_feedback
        pocket.WF._items = []
        pocket.main(None)
        self.assertTrue(len(pocket.WF._items), 1)
        self.assertTrue('archive.com' in pocket.WF._items[0].subtitle)

    def test_main_images(self):
        CachedData['__workflow_update_status'] = {
            'available': False
        }
        CachedData['pocket_list'] = test_data.get_normal()
        sys.argv = ['pocket.py', 'in:images ']

        def send_feedback():
            pass
        pocket.WF.send_feedback = send_feedback
        pocket.WF._items = []
        pocket.main(None)
        self.assertTrue(len(pocket.WF._items), 1)
        self.assertTrue('github.com' in pocket.WF._items[0].subtitle)

    def test_main_mytags(self):
        CachedData['__workflow_update_status'] = {
            'available': False
        }
        CachedData['pocket_list'] = test_data.get_normal()
        CachedData['pocket_tags'] = ['tag1', 'tag2', 'tag3', 'tag4']
        sys.argv = ['pocket.py', 'in:mytags ']

        def send_feedback():
            pass
        pocket.WF.send_feedback = send_feedback
        pocket.WF._items = []
        pocket.main(None)
        self.assertEquals(len(pocket.WF._items), 4)
        self.assertTrue('tag1' in pocket.WF._items[0].title)

    def test_main_mytags_search(self):
        CachedData['__workflow_update_status'] = {
            'available': False
        }
        CachedData['pocket_list'] = test_data.get_normal()
        CachedData['pocket_tags'] = ['interesting', 'tag2', 'tag3', 'tag4']
        sys.argv = ['pocket.py', 'in:mytags interes']

        def send_feedback():
            pass
        pocket.WF.send_feedback = send_feedback
        pocket.WF._items = []
        pocket.main(None)
        self.assertEquals(len(pocket.WF._items), 1)
        self.assertTrue('interesting' in pocket.WF._items[0].title)

    def test_main_random(self):
        CachedData['__workflow_update_status'] = {
            'available': False
        }
        CachedData['pocket_list'] = test_data.get_normal()
        sys.argv = ['pocket.py', 'in:random ']

        def send_feedback():
            pass
        pocket.WF.send_feedback = send_feedback
        pocket.WF._items = []
        pocket.main(None)
        self.assertEquals(len(pocket.WF._items), 3)
        self.assertTrue('0' in pocket.WF._items[0].status)

    def test_main_single_tag(self):
        CachedData['__workflow_update_status'] = {
            'available': False
        }
        CachedData['pocket_list'] = test_data.get_normal()
        CachedData['pocket_tags'] = ['mytag']
        sys.argv = ['pocket.py', 'in:mytags #mytag']

        def send_feedback():
            pass
        pocket.WF.send_feedback = send_feedback
        pocket.WF._items = []
        pocket.main(None)
        self.assertEquals(len(pocket.WF._items), 1)
        self.assertTrue('google.com' in pocket.WF._items[0].subtitle)

    def test_main_error(self):
        CachedData['__workflow_update_status'] = {
            'available': True
        }
        CachedData['pocket_error'] = 'AuthException'
        sys.argv = ['pocket.py', '']

        def send_feedback():
            pass
        pocket.WF.send_feedback = send_feedback
        pocket.main(None)

    def test_main_empty(self):
        CachedData['__workflow_update_status'] = {
            'available': False
        }
        sys.argv = ['pocket.py', 'in:mylist ']

        def send_feedback():
            pass
        pocket.WF.send_feedback = send_feedback
        pocket.WF._items = []
        pocket.main(None)
        self.assertEquals(len(pocket.WF._items), 1)
        self.assertTrue('Pocket list is empty' in pocket.WF._items[0].title)

    def test_register_magic_arguments(self):
        pocket.WF = pocket.Workflow()
        self.assertTrue('deauth' not in pocket.WF.magic_arguments)
        pocket.register_magic_arguments()
        pocket.WF.magic_arguments['deauth']()
        self.assertTrue('deauth' in pocket.WF.magic_arguments)
        self.assertEquals(pocket.WF.magic_prefix, 'wf:')

    def test_get_links(self):
        def cached_data(self, key, max_age=None):
            if 'pocket_list' not in CachedData:
                CachedData['pocket_list'] = 12345
                return None
            return CachedData.get(key)
        pocket.Workflow.cached_data = cached_data
        self.assertEquals(pocket.get_links(), 12345)

        CachedData.clear()
        self.assertEquals(pocket.get_links(tries=0), {})

    def test_add_items(self):
        self.assertEquals(len(pocket.WF._items), 0)
        pocket.add_items(links={}, user_input='')
        self.assertEquals(len(pocket.WF._items), 1)
        self.assertEquals(pocket.WF._items[0].title, 'No links found for "".')

        pocket.WF._items = []
        pocket.add_items(links=[{
            'item_id': '1',
            'given_title': 'test',
            'given_url': 'url',
            'time_added': '10',
        }], user_input='')
        self.assertEquals(len(pocket.WF._items), 1)
        self.assertEquals(pocket.WF._items[0].title, 'test')

        pocket.WF._items = []
        pocket.add_items(links=[{
            'item_id': '1',
            'given_title': 'test',
            'resolved_title': 'test',
            'given_url': 'url',
            'time_added': '10',
            'tags': {'alfred': {'item_id': '4444', 'tag': 'alfred'}}
        }], user_input='notfound')
        self.assertEquals(len(pocket.WF._items), 1)
        self.assertEquals(pocket.WF._items[0].title, "No links found for "
                                                     "\"notfound\".")

    def test_get_auth_url(self):
        expected_start = 'https://getpocket.com/auth/authorize?'
        self.assertTrue(pocket.get_auth_url().startswith(expected_start))

    def setUp(self):
        pocket = pocket_backup
        CachedData.clear()
        Passwords.clear()

        pocket.Workflow.alfred_env = {
            'theme_background': 'rgba(40,40,40,0.1)',
        }

        logging.disable(logging.CRITICAL)

        def cached_data(self, key, max_age=None):
            return CachedData.get(key)
        pocket.Workflow.cached_data = cached_data

        def cache_data(self, key, data):
            CachedData[key] = data
        pocket.Workflow.cache_data = cache_data

        def get_password(self, key):
            return Passwords.get(key)
        pocket.Workflow.get_password = get_password

        def delete_password(self, key):
            if key in Passwords:
                del Passwords[key]
        pocket.Workflow.delete_password = delete_password

        def refresh_list():
            pass
        pocket.refresh_list = refresh_list


if __name__ == "__main__":
    unittest.main()
