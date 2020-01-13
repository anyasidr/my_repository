import indexer
import os

def make(dir = 'books', files=[], db_name='mydb'):
    i = indexer.Indexator(db_name)
    for f in files:
        print(f)
        i.indextie_with_lines(f)

def make_from_dir(dir='books', db_name='database\\mydb'):
    i = indexer.Indexator(db_name)
    files = os.listdir(dir)
    for f in files:
        print(dir + "\\" + f)
        i.indextie_with_lines(dir + "\\" + f)

make_from_dir('books', 'database\\database')
