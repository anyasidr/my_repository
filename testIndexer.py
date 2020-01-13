import unittest
import moytokenizer
import os
import shelve
from indexer import Indexator, Position


class TestIndexator(unittest.TestCase):
    def setUp(self):
        self.indexator = Indexator('database')
        
    def test_digit(self):
        with self.assertRaises(TypeError):
            self.indexator.indextie(123456)
            
    def test_input(self):
        with self.assertRaises(FileNotFoundError):
            self.indexator.indextie('lalala')
            
    def test_filename(self):
        with self.assertRaises(FileNotFoundError):
            self.indexator.indextie('lalala.txt')     

    def test_one_word(self):      
        file = open('test.txt', 'w')
        file.write('indexator')
        file.close()        
        self.indexator.indextie('test.txt')        
        data_dict = dict(shelve.open('database'))
        dictionary = {'indexator': {'test.txt': [Position(0, 9)]}}
        self.assertEqual(data_dict, dictionary)
        
    def test_many_words(self):      
        file = open('test.txt', 'w')
        file.write('testing my indexator')
        file.close()        
        self.indexator.indextie('test.txt')        
        data_dict = dict(shelve.open('database'))
        dictionary = {
            'testing': {
                'test.txt': [Position(0, 7)]
            },
            'my': {
                'test.txt': [Position(8, 10)]
            },
            'indexator': {
                'test.txt': [Position(11, 20)]}}
        self.assertEqual(data_dict, dictionary) 

    def test_two_files(self):      
        file1 = open('test1.txt', 'w')
        file1.write('file number one')
        file1.close()        
        self.indexator.indextie('test1.txt')        
        test2 = open('test2.txt', 'w')
        test2.write('file number two')
        test2.close() 
        self.indexator.indextie('test2.txt')
        data_dict = dict(shelve.open('database'))
        dictionary = {
            'file': {
                'test1.txt': [Position(0, 4)],
                'test2.txt': [Position(0, 4)]
            },
            'number': {
                'test1.txt': [Position(5, 11)],
                'test2.txt': [Position(5, 11)]
            },
            'one': {
                'test1.txt': [Position(12, 15)]
            },
            'two': {
                'test2.txt': [Position(12, 15)]}}
        self.assertEqual(data_dict, dictionary)

    def tearDown(self):
        del self.indexator
        for filename in os.listdir(os.getcwd()):            
            if filename == 'database' or filename.startswith('database.'):
                os.remove(filename)        
        if 'test.txt' in os.listdir(os.getcwd()):
            os.remove('test.txt')
        if 'test1.txt' in os.listdir(os.getcwd()):
            os.remove('test1.txt')
        if 'test2.txt' in os.listdir(os.getcwd()):
            os.remove('test2.txt')


if __name__=='__main__':
    unittest.main()
