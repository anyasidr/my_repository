from moytokenizer import Tokenizer
import shelve
import os


class Position(object):
    """
    This class contains positions of tokens that are
    alphas and digits. Positions consist of beginnings
    and endings of tokens.
    """
  
    def __init__(self, start, end):
        """
        method that creates an example of
        class Position.
        """
        self.start = start
        self.end = end

    def __eq__(self, obj):
        """
        method that compares tokens by their
        initial and final positions.
        """
        return self.start == obj.start and self.end == obj.end

    def __repr__(self):
        """
        This method provides an appropriate 
        representation.
        """
        return '(' + str(self.start) + ';' + ' ' + str(self.end) + ')'


class Position_with_lines(object):
    """
    This class contains positions of the first and 
    last symbol of each token and also the number
    of its line.
    """
    
    def __init__(self, start, end, line):
        """
        method that creates an example of
        class Position_with_lines.
        """
        self.start = start
        self.end = end
        self.line = line

    def __eq__(self, obj):
        """
        method that compares tokens by their
        initial and final positions and also
        by their number of lines.
        """
        return (self.start == obj.start and self.end == obj.end and
                self.line == obj.line)

    def __repr__(self):
        """
        This method provides an appropriate 
        representation.
        """
        return '(' + str(self.start) + ', ' + str(self.end) + ', ' + str(self.line) + ')'


class Indexator(object):
    """
    This class is used for indexing text.
    Indexing means to create a database that will
    contain positions of all tokens in given text. 
    """
    
    def __init__(self, db_name):
        """
        method that creates an example
        of class Indexator.
        """
        self.database = shelve.open(db_name, writeback=True)

    def indextie(self, filename):
        """
        This method indexties text that is stored
        in some file. The method opens the file,
        indexties the text and puts all tokens with their
        positions in a database.
        """
        if not isinstance(filename, str):
            raise TypeError('Inappropriate type')
        text = open(filename)
        tokenizer = Tokenizer()
        for word in tokenizer.for_index_tokenize(text.read()): 
            self.database.setdefault(word.text, {}).setdefault(filename, []).append(Position(word.position,
            (word.position + len(word.text))))
        text.close()
        self.database.sync()

    def indextie_with_lines(self, filename):
        """
        This method indexties text that is stored
        in some file. The method opens the file,
        indexties the text and puts all tokens with their
        positions and number of the line of in a database.
        """
        if not isinstance(filename, str):
            raise TypeError('Inappropriate type')
        text = open(filename)
        tokenizer = Tokenizer()
        for number, line in enumerate(text):
            for word in tokenizer.for_index_tokenize(line):
                self.database.setdefault(word.text, {}).setdefault(filename, []).append(Position_with_lines
                (word.position, (word.position + len(word.text)), number))
        text.close()
        self.database.sync()

    def __del__(self):
        """
        the method closes our database.
        """
        self.database.close()

def main():
    indexator = Indexator('database')
    file = open('text.txt', 'w')
    file.write('well well well')
    file.close()
    indexator.indextie_with_lines('text.txt')
    del indexator
    os.remove('text.txt')
    print(dict(shelve.open('database')))
    for filename in os.listdir(os.getcwd()):
        if filename == 'database' or filename.startswith('database.'):
            os.remove(filename)


if __name__=='__main__':
    main()
