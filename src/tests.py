import unittest

import pocket_refresh

class PocketTestCase(unittest.TestCase):

   def test_sync_data(self):
        links = {}

        data = {}
        links = pocket_refresh.sync_data(links, data)
        self.assertEquals(links, {})

        data = {
            '1234': {'status': '0'},
            '5678': {'status': '0'},
        }
        links = pocket_refresh.sync_data(links, data)
        self.assertTrue('1234' in links)
        self.assertTrue('5678' in links)
        self.assertEquals(len(links.keys()), 2)

        data = {
            '5678': {'status': '1'},
        }
        links = pocket_refresh.sync_data(links, data)
        self.assertTrue('1234' in links)
        self.assertFalse('5678' in links)



if __name__ == "__main__":
    unittest.main()
