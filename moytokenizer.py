"""This module is used for tokenizing strings.
The string must be divided into alphabetic characters.""" 

import re
"""
importing the module of regular expressions
"""
import unicodedata


class Token(object):
    """
    this class represents tokens aka alphabetic sequences
    """
    def __init__(self, position, text):
        """
        position is a position of each first character of a token
        text is a representation of tokens
        """
        self.position = position
        self.text = text
        

class TokenwithType(Token):
    """
    this class represents tokens with types
    """

    def __init__(self, position, text, typ):
        """
        position is a position of each first character of a token
        text is a representation of tokens
        type is a type of the token
        """
        self.position = position
        self.text = text
        self.typ = typ

        
class Tokenizer(object):
    """
    this class uses method tokenize to tokenize a string
    """
    def __init__(self):
        """
        this method makes groups of letters
        """
        # searching for alphabetic sequences only
        self.pattern = re.compile("[^\W\d]+") 
        
    def tokenize(self, text):
        """
        this method divides a string into tokens
        consisting of alphabetic symbols
        @param text: string that'll be divided into tokens
        @return: list of tokens
        """
        if not type(text) is str:
            raise ValueError
        tokens = []
        # searching for pattern in a string
        for match in self.pattern.finditer(text):
                # extracting tokens with their positions
                token = Token(match.start(), match.group())
                tokens.append(token)
        return tokens

    def gen_tokenize(self, text):
        """
        this method divides a string into tokens
        consisting of alphabetic symbols
        @param text: string that'll be divided into tokens
        @return: generator
        """
        if not type(text) is str:
            raise ValueError
        # searching for pattern in a string
        for match in self.pattern.finditer(text):
            # extracting tokens with their positions 
            token = Token(match.start(), match.group())
            yield token

    @staticmethod
    def Type(c):
        """
        this method defines a type of the character
        """
        if c.isalpha():
            typ='a'
        
        elif c.isdigit():
            typ= 'd'
        
        elif c.isspace():
            typ='s'
        
        elif unicodedata.category(c)[0] == 'P':
            typ='p'
        else:
            typ = 'o'
        return typ

    def gen_type_tokenize(self,text):
        """
        this method divides a string into tokens consisting of
        different types of characters
        @param text: string that'll be divided into tokens
        @return: generator
        """
        
        if not isinstance(text, str):
            raise ValueError
        
        if text == "":
            return
        
        pos = 0
        for index, character in enumerate(text):
            # definiton of the current type
            ctype = self.Type(character)
            # definition of the previous type
            ptype = self.Type(text[index-1])
            # check if the type of the current character is
            # different from the type of the previous character
            if ctype != ptype:
                typ = ptype
                word = text[pos:index]
                token = TokenwithType(pos, word, typ)
                yield token
                pos = index
            # looking for the last character
            typ = ctype
            word = text[pos:index+1]
            token = TokenwithType(pos, word, typ)
        yield token

    def for_index_tokenize(self, string):
            for word in self.gen_type_tokenize(string):
                if word.typ == 'a' or word.typ == 'd':
                    yield word
        

if __name__ == '__main__':
    text = "доброе утро44 !!! - ++ 6&13 **(   спокойной темно-синий  441 ночи привет. Стол - это предмет мебели"

    words = Tokenizer().tokenize(text)
    for token in words:
        print(token.text, token.position)
    gen_words = Tokenizer().gen_tokenize(text)
    for token in gen_words:
        print(token.text, token.position)
    gen_type_words = Tokenizer()
    tokens = list(gen_type_words.gen_type_tokenize(text))
    for token in tokens:
        print(token.text, token.position, token.typ)
    

    





        



