#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import unittest

from full_text_local import FullText

CachedData = {}
Passwords = {}


class PocketFullTextLocalTestCase(unittest.TestCase):

    def test_refresh(self):
        cases = {
            u'https://askubuntu.com/questions/798516/what-tool-adds-unlimited-clipboard-and-searchable-retrieval':
                [
                    u'ALFRED Powerpack',
                    u'ALFRED Power',
                    u'clipboard manager',
                    u'clipboard manag',
                    u'clipboard man',
                ],
            u'https://www.zhihu.com/question/20186320':
                [
                    u'Pocket',
                    u'有自己的图片服务器',
                    u'有自己的图片服务',
                ],
            u'https://www.quora.com/What-does-Andrew-Ng-think-about-Deep-Learning':
                [
                    u'algorithms that can take advantage',
                    u'algorithms that can take advant',
                    u'AI made tremendous',
                    u'AI made tremend',
                ],

        }
        for url, keywords in cases.items():
            FullText.get_instance().del_page(url)
            FullText.get_instance().add_page(url)
            for keyword in keywords:
                self.assertTrue(url in {item['url'] for item in FullText.get_instance().search(keyword)})

    def test_wrong_url(self):
        cases = {
            u'https://askubuu.cm/questions/798516/what-tool-adds-unlimited-clipboard-and-searchable-retrieval':
                [u'ALFRED Powerpack', u'clipboard manager'],
            u'https://www.zhdu.com/question/20186320':
                [u'Pocket', u'有自己的图片服务器'],
            u'https://www.qurdfdfdfdfa.com/What-does-Andrew-Ng-think-about-Deep-Learning':
                [u'algorithms that can take advantage', u'AI made tremendous'],

        }
        for url, keywords in cases.items():
            FullText.get_instance().del_page(url)
            FullText.get_instance().add_page(url)
            for keyword in keywords:
                self.assertTrue(url not in {item['url'] for item in FullText.get_instance().search(keyword)})

    def test_delete_docs(self):
        cases = {
            u'https://askubuntu.com/questions/798516/what-tool-adds-unlimited-clipboard-and-searchable-retrieval':
                [u'ALFRED Powerpack', u'clipboard manager'],
            u'https://www.zhihu.com/question/20186320':
                [u'Pocket', u'有自己的图片服务器'],
            u'https://www.quora.com/What-does-Andrew-Ng-think-about-Deep-Learning':
                [u'algorithms that can take advantage', u'AI made tremendous'],

        }
        for url, keywords in cases.items():
            FullText.get_instance().add_page(url)
            FullText.get_instance().del_page(url)
            for keyword in keywords:
                self.assertTrue(url not in {item['url'] for item in FullText.get_instance().search(keyword)})


if __name__ == "__main__":
    unittest.main()
