#!/usr/bin/env python
# -*- coding: utf-8 -*-
from builtins import str
import gzip
from io import open
import os
import unittest

import msgpack

from ahocorapy.keywordtree import KeywordTree


class TestAhocorapy(unittest.TestCase):

    def test_empty_tree(self):
        kwtree = KeywordTree()
        kwtree.finalize()

        result = kwtree.search('zef')
        self.assertIsNone(result)

    def test_empty_input(self):
        kwtree = KeywordTree()
        kwtree.add('bla')
        kwtree.finalize()

        result = kwtree.search('')
        self.assertIsNone(result)

    def test_empty_keyword(self):
        kwtree = KeywordTree()
        kwtree.add('')
        kwtree.finalize()

        result = kwtree.search('')
        self.assertIsNone(result)

    def test_readme_example(self):
        '''
        As used in the projects README. If you have to change this test case,
        please update the README accordingly.
        '''
        kwtree = KeywordTree(case_insensitive=True)
        kwtree.add('malaga')
        kwtree.add('lacrosse')
        kwtree.add('mallorca')
        kwtree.add('mallorca bella')
        kwtree.finalize()

        result = kwtree.search('My favorite islands are malaga and sylt.')
        self.assertEqual(('malaga', 24), result)

        result = kwtree.search(
            'idontlikewhitespaceswhereismalacrossequestionmark')
        self.assertEqual(('lacrosse', 29), result)

        result = kwtree.search('crossing on mallorca bella')
        self.assertEqual(('mallorca', 12), result)

    def test_suffix_stuff(self):
        kwtree = KeywordTree()
        kwtree.add('blaaaaaf')
        kwtree.add('bluez')
        kwtree.add('aaaamen')
        kwtree.add('uebergaaat')
        kwtree.finalize()

        result = kwtree.search('blaaaaamentada')
        self.assertEqual(('aaaamen', 3), result)

        result = kwtree.search('clueuebergaaameblaaaamenbluez')
        self.assertEqual(('aaaamen', 17), result)

    def test_text_end_situation(self):
        kwtree = KeywordTree()
        kwtree.add('blaaaaaf')
        kwtree.add('a')
        kwtree.finalize()

        result = kwtree.search('bla')
        self.assertEqual(('a', 2), result)

    def test_text_end_situation_2(self):
        kwtree = KeywordTree()
        kwtree.add('blaaaaaf')
        kwtree.add('la')
        kwtree.finalize()

        result = kwtree.search('bla')
        self.assertEqual(('la', 1), result)

    def test_simple(self):
        kwtree = KeywordTree()
        kwtree.add('bla')
        kwtree.add('blue')
        kwtree.finalize()

        result = kwtree.search('bl')
        self.assertIsNone(result)

        result = kwtree.search('')
        self.assertIsNone(result)

        result = kwtree.search('zef')
        self.assertIsNone(result)

        result = kwtree.search('blaaaa')
        self.assertEqual(('bla', 0), result)

        result = kwtree.search('red green blue grey')
        self.assertEqual(('blue', 10), result)

    def test_simple_back_to_zero_state_example(self):
        kwtree = KeywordTree()
        keyword_list = ['ab', 'bca']
        for keyword in keyword_list:
            kwtree.add(keyword)
        kwtree.finalize()

        result = kwtree.search('blbabca')
        self.assertEqual(('ab', 3), result)

    def test_domains(self):
        kwtree = KeywordTree()
        kwtree.add('searchenginemarketingfordummies.com')
        kwtree.add('linkpt.com')
        kwtree.add('fnbpeterstown.com')
        kwtree.finalize()

        result = kwtree.search('peterchen@linkpt.com')
        self.assertEqual(('linkpt.com', 10), result)

    def test_unicode(self):
        kwtree = KeywordTree()
        kwtree.add('bla')
        kwtree.add('blue')
        kwtree.add(u'颜到')
        kwtree.finalize()

        result = kwtree.search(u'春华变苍颜到处群魔乱')
        self.assertEqual((u'颜到', 4), result)

        result = kwtree.search(u'三年过')
        self.assertIsNone(result)

    def test_case_sensitivity(self):
        kwtree = KeywordTree()
        kwtree.add('bla')
        kwtree.add('blue')
        kwtree.add('blISs')
        kwtree.finalize()

        result = kwtree.search('bLa')
        self.assertIsNone(result)

        result = kwtree.search('BLISS')
        self.assertIsNone(result)

        result = kwtree.search('bliss')
        self.assertIsNone(result)

        result = kwtree.search('blISs')
        self.assertEqual(('blISs', 0), result)

    def test_case_insensitivity_mode(self):
        kwtree = KeywordTree(case_insensitive=True)
        kwtree.add('bla')
        kwtree.add('blue')
        kwtree.add('blISs')
        kwtree.finalize()

        result = kwtree.search('bLa')
        self.assertEqual(('bla', 0), result)

        result = kwtree.search('BLISS')
        self.assertEqual(('blISs', 0), result)

    def test_dump_and_load(self):
        kwtree = KeywordTree(case_insensitive=True)
        kwtree.add('bla')
        kwtree.add('blue')
        kwtree.add('blISs')
        kwtree.finalize()

        filename = 'kwtree_unittest.msgpack.gz'

        dumped = kwtree.dump()
        with gzip.open(filename, 'wb') as output_file:
            msgpack.dump(dumped, output_file, use_bin_type=True)

        with gzip.open(filename, 'rb') as input_file:
            loadedTree = msgpack.load(input_file, encoding='utf-8')
        kwtree2 = KeywordTree()
        kwtree2.load(loadedTree)

        result = kwtree2.search('bLa')
        self.assertEqual(('bla', 0), result)

        result = kwtree2.search('BLISS')
        self.assertEqual(('blISs', 0), result)

        try:
            os.remove(filename)
        except OSError:
            pass

    def test_utility_calls(self):
        kwtree = KeywordTree(case_insensitive=True)
        kwtree.add('bla')
        kwtree.add('blue')
        kwtree.finalize()
        # Just test that there are no errors
        rep = repr(kwtree)
        self.assertGreater(len(rep), 0)
        tostring = str(kwtree)
        self.assertGreater(len(tostring), 0)

    def test_finalize_errors(self):
        kwtree = KeywordTree(case_insensitive=True)
        kwtree.add('bla')
        kwtree.add('blue')

        self.assertRaises(ValueError, kwtree.search, 'blueb')

        kwtree = KeywordTree(case_insensitive=True)
        kwtree.add('bla')
        kwtree.finalize()

        self.assertRaises(ValueError, kwtree.add, 'blueb')

        kwtree = KeywordTree(case_insensitive=True)
        kwtree.add('bla')
        kwtree.finalize()

        self.assertRaises(ValueError, kwtree.finalize)

    def test_many_keywords(self):
        kwtree = KeywordTree(case_insensitive=True)
        with open('tests/data/names.txt') as keyword_file:
            keyword_list = list(map(str.strip, keyword_file.readlines()))

        for kw in keyword_list:
            kwtree.add(kw)

        kwtree.finalize()
        with open('tests/data/textblob.txt') as keyword_file:
            textblob = keyword_file.read()

        result = kwtree.search(textblob)
        self.assertEqual(('Dawn Higgins', 34153), result)


if __name__ == '__main__':
    unittest.main()
