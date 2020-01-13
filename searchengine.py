import shelve
import os
import indexer
import re
import windows
from moytokenizer import Tokenizer
from indexer import Position_with_lines


class SearchEngine(object):
    """
    This class is used for searching of
    positions of tokens in a given database.
    """
    
    def __init__(self, dbname):
        """
        This method creates an example of 
        class SearchEngine.
        """
        self.database = shelve.open(dbname, writeback=True)
        # print(dict(self.database))
        self.tokenizer = Tokenizer()

    def search_one(self, query):
        """
        This method searches in a database. The method uses
        a key that is a tokens, returns all the positions
        of the token.
        """
        if not isinstance(query, str):
            raise ValueError
        return self.database.get(query, {})

    def search_many(self, query):
        """
        This method uses tokenization. The method searches in a database, 
        finds tokens in a tokenized string. Returns a dictionary where
        the tokens are keys with their positions in all given files.
        """
        if not isinstance(query, str):
            raise ValueError
        if query == '':
            return {}
        
        tokenizer = Tokenizer() # using tokenizer for extracting tokens
        words = list(tokenizer.for_index_tokenize(query))
        results = [] # creating a tuple
        for word in words:
            results.append(self.database[word.text])   
        files = set(results[0]) # converting tuple into set
        for result in results:
            files &= set(result) # intersecting sets of documents
        positions = {} # creating a dictionary with positions
        for file in files:
            for result in results:
                  positions.setdefault(file, []).extend(result[file])
        return positions

    def get_window(self, in_dict, size=3):
        """
        Сreate dictionary of files and context windows
        """
        if not (isinstance(in_dict, dict) and
                isinstance(size, int)):
            raise ValueError
        
        conts_dict = {}
        for f, positions in in_dict.items():
            for position in positions:
                cont = windows.ContextWindow.find_window(f, position, size)
                conts_dict.setdefault(f, []).append(cont)
        joined_conts_dict = self.join_windows(conts_dict)
        return joined_conts_dict

    def join_windows(self, in_dict):
        """
        Join cross windows in a dictionary of files

        @param in_dict: dict to join
        """
        conts_dict = {}
        empty = windows.ContextWindow([], "", 0, 0)
        for f, conts in in_dict.items():
            previous_cont = empty
            for cont in conts:
                if previous_cont.is_cross(cont):
                    previous_cont.join_cont(cont)
                else:
                    if previous_cont is not empty:
                        conts_dict.setdefault(f, []).append(previous_cont)
                    previous_cont = cont
            conts_dict.setdefault(f, []).append(previous_cont)
        return conts_dict

    def search_to_window(self, query, size=3):
        """
        Search query words in database
        """
        positions_dict = self.search_many(query)
        cont_dict = self.get_window(positions_dict, size)
        return cont_dict

    def search_to_sentence(self, query, size=3):
        """
        Search multiword query in database
        """
        context_dict = self.search_to_window(query, size)
        for contexts in context_dict.values():
            for context in contexts:
                context.expand_cont()
        sentence_dict = self.join_windows(context_dict)
        return sentence_dict

    def search_to_highlight(self, query, size=3):
        """
        Search multiword query in database and highlighting them with 
        <strong> tag
        """
        sentence_dict = self.search_to_sentence(query, size)
        quote_dict = {}
        for f, conts in sentence_dict.items():
            for cont in conts:
                quote_dict.setdefault(f, []).append(cont.highlight())
        return quote_dict

    def search_limit_offset(self, query, size=3, doclimit=0, docoffset=0, limits=[], offsets=[]):
        '''
        filter result
        :param query:
        :param size:
        :param doclimit: documents limit (0..4)
        :param docoffset: documents offset (0..4)
        :param limits: list of limits in document
        :param offsets: list of offsets in document
        :return:
        '''
        r = self.search_to_highlight(query, size)
        j = 0
        myres = {}
        key_list = list(r.keys())
        key_list.sort()
        for key in key_list:
            myres[key] = []
            if (j >= int(docoffset)) and (j < int(docoffset) + int(doclimit)):
                i = 0
                for val in r[key]:
                    if (i >= int(offsets[j])) and (i < int(offsets[j]) + int(limits[j])):
                        myres[key].append(val)
                    i = i + 1
            j = j + 1
        return myres

    # task acc0 - add to all functions limit and offset parameters
    def search_many_limit_offset(self, query, limit=0, offset=0, limits=[], offsets=[]):
        '''
        this function for filtering result search many with limit and offset parameters
        (task acc0)
        :param query: multiword query
        :param limit: limit of documents
        :param offset: offset of documents
        :return:
        '''
        if not isinstance(query, str):
            raise ValueError
        if not isinstance(limit, int):
            raise ValueError
        if not isinstance(offset, int):
            raise ValueError
        for lim in limits:
            if not isinstance(lim, int):
                raise ValueError
        for of in offsets:
            if not isinstance(of, int):
                raise ValueError
        if query == '':
            return {}
        if offset < 0:
            offset = 0
        if limit < 0:
            limit = 0
        tokenizer = Tokenizer()  # using tokenizer for extracting tokens
        words = list(tokenizer.for_index_tokenize(query))
        results = []  # creating a tuple
        for word in words:
            results.append(self.database[word.text])
        files = sorted(set(results[0]))  # converting tuple into set
        i = 0
        filtered = set([])
        for file in files:
            if (i >= int(offset)) and (i < (int(offset) + int(limit))):
                filtered.add(file)
            i = i + 1
        files = filtered
        for result in results:
            files &= set(result)  # intersecting sets of documents
        files = sorted(files)
        positions = {}  # creating a dictionary with positions
        i = 0
        for file in files:
            for result in results:
                k = i + offset
                positions.setdefault(file, []).extend(result[file][offsets[k]: limits[k]+offsets[k]])
            i = i + 1
        return positions

    def search_to_window_limit_offset(self, query, size=3, limit=0, offset=0, limits=[], offsets=[]):
        """
        Search query words in database with limit and offset parameters
        """
        positions_dict = self.search_many_limit_offset(query, limit, offset, limits, offsets)
        cont_dict = self.get_window(positions_dict, size)
        return cont_dict

    def search_to_sentence_limit_offset(self, query, size=3, limit=0, offset=0, limits=[], offsets=[]):
        """
        Search multiword query in database with limit and offset parameters
        """
        context_dict = self.search_to_window_limit_offset(query, size, limit, offset, limits, offsets)
        for contexts in context_dict.values():
            for context in contexts:
                context.expand_cont()
        sentence_dict = self.join_windows(context_dict)
        return sentence_dict

    def search_to_highlight_limit_offset(self, query, size=3, limit=0, offset=0, limits=[], offsets=[]):
        """
        Search multiword query in database and highlighting them with
        <strong> tag
        """
        int_limits = []
        for lim in limits:
            int_limits.append(int(lim))
        int_offsets = []
        for of in offsets:
            int_offsets.append(int(of))
        sentence_dict = self.search_to_sentence_limit_offset(query, size, int(limit), int(offset), int_limits, int_offsets)
        quote_dict = {}
        for f, conts in sentence_dict.items():
            for cont in conts:
                quote_dict.setdefault(f, []).append(cont.highlight())
        files = os.listdir('books\\')
        for f in files:
            if not(('books\\'+f) in quote_dict.keys()):
                quote_dict['books\\'+f] = []
        return quote_dict


    def close(self):
        """
        methos closes database.
        """
        self.database.close()

def main():    
    i = indexer.Indexator('db_name')    
    file1 = open('test1.txt', 'w')
    file1.write('Да, это пустые слова, здесь нет ничего полезного. привет как твои дела ? у меня все хорошо, я хочу домой приди ко мне! но ты же не свободна?')
    file1.close()
    file2 = open('test2.txt', 'w')
    file2.write('да я хочу сказать тебе . привет и все, но зачем все привет эти слова? я хочу быть счастливым! И точка')
    file2.close()
    i.indextie_with_lines('test1.txt')
    i.indextie_with_lines('test2.txt')
    del i
    search_engine = SearchEngine('db_name')
    #result = search_engine.search_many('my test')
    #print(result)

    r = search_engine.search_to_highlight('привет', 4)
    print(r)

    """i = indexer.Indexator('tolstoy')
    i.indextie_with_lines('tolstoy1.txt')
    del i
    search_engine = SearchEngine('tolstoy')
    r = search_engine.search_to_highlight('Анна', 4)
    for key in r.keys():
        for val in r[key]:
            print (val)"""


    del search_engine
    if 'test1.txt' in os.listdir(os.getcwd()):
        os.remove('test1.txt')
    if 'test2.txt' in os.listdir(os.getcwd()):
        os.remove('test2.txt')
    for filename in os.listdir(os.getcwd()):            
        if filename == 'db_name' or filename.startswith('db_name.'):
            os.remove(filename) 
    

            
if __name__=='__main__':
    main()
