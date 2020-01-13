import unittest
import make_db
import shelve
import os
from indexer import Indexator, Position, Position_with_lines
from searchengine import SearchEngine
from windows import ContextWindow

test1 = "this is my test"
test2 = "my test"

database = {'this': {'test1.txt': [Position_with_lines(0, 4, 0)]},
            'is': {'test1.txt': [Position_with_lines(5, 7, 0)]},
            'my': {'test1.txt': [Position_with_lines(8, 10, 0)],
                   'test2.txt': [Position_with_lines(0, 2, 0)]},
            'test': {'test1.txt': [Position_with_lines(11, 15, 0)],
                     'test2.txt': [Position_with_lines(3, 7, 0)]}}


class TestContextWindow(unittest.TestCase):

    def setUp(self):
        with open("test1.txt", 'w') as file:
            file.write(test1)
        with open("test2.txt", 'w') as file:
            file.write(test2)

    # def test_input(self):
    #     with self.assertRaises(ValueError):
    #         ContextWindow.find_window(0, 0, 50)

    def test_wrong_line(self):
        with self.assertRaises(ValueError):
            ContextWindow.find_window("test1.txt", Position_with_lines(0, 4, 3), 3)

    def test_one(self):
        result = ContextWindow.find_window("test1.txt", Position_with_lines(5, 7, 0), 1)
        self.assertEqual(result.position, [Position_with_lines(5, 7, 0)])
        self.assertEqual(result.start, 0)
        self.assertEqual(result.end, 10)
        self.assertEqual(result.line, test1)

    def test_no_context(self):
        result = ContextWindow.find_window("test1.txt", Position_with_lines(5, 7, 0), 0)
        self.assertEqual(result.position, [Position_with_lines(5, 7, 0)])
        self.assertEqual(result.start, 5)
        self.assertEqual(result.end, 7)
        self.assertEqual(result.line, test1)

    
    def test_join(self):
        query1 = ContextWindow.find_window('test1.txt', Position_with_lines(5, 7, 0), 1)
        query2 = ContextWindow.find_window('test1.txt', Position_with_lines(11, 15, 0), 1)
        result = query1.join_cont(query2)
        self.wnd = ContextWindow('this is my test', [Position_with_lines(5, 7, 0), Position_with_lines(11, 15, 0)], 0, 15)
        self.assertEqual(query1.start, self.wnd.start)
        self.assertEqual(query1.end, self.wnd.end)
        self.assertEqual(query1.line, self.wnd.line)
        os.remove('test1.txt')

    def test_highlight(self):
        query = ContextWindow.find_window('test1.txt', Position_with_lines(5, 7, 0), 1)
        result = query.highlight()
        text = 'this <strong>is</strong> my'
        self.assertEqual(result, text)

    def tearDown(self):
        if 'test1.txt' in os.listdir(os.getcwd()):
            os.remove('test1.txt')
        if 'test2.txt' in os.listdir(os.getcwd()):
            os.remove('test2.txt')


class TestSearchEngine(unittest.TestCase):
    def make_db_test(self):
        with open("test1.txt", 'w') as file:
            file.write(test1)
        with open("test2.txt", 'w') as file:
            file.write(test2)
        make_db.make(['test1.txt', 'test2.txt'], 'db_name')
        result = open('db_name.dir', 'r').read()
        self.assertEqual(result, "'this', (0, 107)\n'is', (512, 107)\n'my', (1024, 152)\n'test', (1536, 152)")

    def tearDown(self):
        for filename in os.listdir(os.getcwd()):
            if filename == 'db_name' or filename.startswith('db_name'):
                os.remove(filename)
        if 'test1.txt' in os.listdir(os.getcwd()):
            os.remove('test1.txt')
        if 'test2.txt' in os.listdir(os.getcwd()):
            os.remove('test2.txt')


class TestSearchEngine(unittest.TestCase):
    def setUp(self):
        self.engine = SearchEngine('db_name')
        self.engine.database.update(database)
        with open("test1.txt", 'w') as file:
            file.write(test1)
        with open("test2.txt", 'w') as file:
            file.write(test2)
        make_db.make(['test1.txt', 'test2.txt'], 'db_name')

    def test_empty(self):
        result = self.engine.search_one('')
        self.assertEqual(result, {})

    def test_search_one(self):
        result = self.engine.search_one('test')
        self.assertEqual(result, {'test1.txt': [Position_with_lines(11, 15, 0)],
                                  'test2.txt': [Position_with_lines(3, 7, 0)]})

    def test_search_many_one(self):
        result = self.engine.search_many('test')
        self.assertEqual(result, {'test1.txt': [Position_with_lines(11, 15, 0)],
                                  'test2.txt': [Position_with_lines(3, 7, 0)]})

    def test_search_many_two(self):
        result = self.engine.search_many('my test')
        self.assertEqual(result, {'test1.txt': [Position_with_lines(8, 10, 0),
                                               Position_with_lines(11, 15, 0)],
                                  'test2.txt': [Position_with_lines(0, 2, 0),
                                               Position_with_lines(3, 7, 0)]})

    def test_search_limit_offset_default(self):
        result = self.engine.search_limit_offset('test')
        self.assertEqual(result, {'test1.txt': [], 'test2.txt': []})

    def test_search_limit_offset_all(self):
        result = self.engine.search_limit_offset('test', doclimit=2, docoffset=0, limits=[2, 2], offsets=[0, 0])
        self.assertEqual(result, {'test1.txt': ['this is my <strong>test</strong>'], 'test2.txt': ['my <strong>test</strong>']})

    def test_search_limit_offset_one(self):
        result = self.engine.search_limit_offset('test', doclimit=1, docoffset=0, limits=[2, 2], offsets=[0, 0])
        self.assertEqual(result, {'test1.txt': ['this is my <strong>test</strong>'], 'test2.txt': []})

    def test_search_limit_offset_shift(self):
        result = self.engine.search_limit_offset('test', doclimit=2, docoffset=1, limits=[2, 2], offsets=[0, 0])
        self.assertEqual(result, {'test1.txt': [], 'test2.txt': ['my <strong>test</strong>']})

    def test_search_many_limit_offset_one(self):
        result = self.engine.search_many_limit_offset('test', limit=1, offset=0)
        self.assertEqual(result, {'test1.txt': [Position_with_lines(11, 15, 0)]})

    def test_search_many_limit_offset_shift(self):
        result = self.engine.search_many_limit_offset('test', limit=1, offset=1)
        self.assertEqual(result, {'test2.txt': [Position_with_lines(3, 7, 0)]})

    def test_search_many_limit_offset_all(self):
        result = self.engine.search_many_limit_offset('test', limit=2, offset=0)
        self.assertEqual(result, {'test1.txt': [Position_with_lines(11, 15, 0)],
                                  'test2.txt': [Position_with_lines(3, 7, 0)]})



    def tearDown(self):
        del self.engine
        for filename in os.listdir(os.getcwd()):
            if filename == 'db_name' or filename.startswith('db_name'):
                os.remove(filename)
        if 'test1.txt' in os.listdir(os.getcwd()):
            os.remove('test1.txt')
        if 'test2.txt' in os.listdir(os.getcwd()):
            os.remove('test2.txt')

if __name__ == '__main__':
    unittest.main()





        




