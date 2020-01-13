import shelve
import os
import indexer
import re
from moytokenizer import Tokenizer
from indexer import Position_with_lines


class ContextWindow(object):
    """
    This class is used to store context windows data
    """
    def __init__(self, line, position, start, end):
        """
        method creates an instance of ContextWindow class
        params:
        position: list of positions of words for context window
        line: string that contains the word for context
        start: position of the first character of the context window
        end: position after the last character of the context window
        """
        self.line = line
        self.position = position
        self.start = start
        self.end = end 

    @classmethod
    def find_window(cls, filename, position, size):
        """
        method creates an instance of class ContextWindow loading from file
        @param filename: path to the file with the word
        @param position: position of the searching word in context window
        @param size: size of the context window
        """
        t = Tokenizer()        
        with open(filename) as f:
            for i, line in enumerate(f):
                if i == position.line:
                    break
        if i != position.line:
            raise ValueError('Inappropriate number')
        line = line.strip("\n")
        positions = [position]        
        right = line[position.start:]
        left = line[:position.end][::-1]
        
        for i, token in enumerate(t.for_index_tokenize(left)):
            if i == size:
                break
        start = position.end - token.position - len(token.text)
        for i, token in enumerate(t.for_index_tokenize(right)):
            if i == size:
                break
        end = position.start + token.position + len(token.text)
        return cls(line, positions, start, end)

    def is_cross(self, wnd):
        """
        Check cross of two context windows

        @param wnd: context window to check
        """
        return (self.start <= wnd.end and
                self.end >= wnd.start and
                wnd.line == self.line)

    def join_cont(self, wnd):
        """
        Join context windows and set it to self

        @param wnd: context window to join
        """
        for position in wnd.position:
            if position not in self.position:
                self.position.append(position)
        self.start = min(self.start, wnd.start)
        self.end = max(self.end, wnd.end)

    def expand_cont(self):
        """
        Expand context window to sentence
        """
        first = re.compile(r'[.!?]\s[A-ZА-Яa-zа-я]')
        last = re.compile(r'[A-ZА-Яa-zа-я]\s[.!?]')
        right = self.line[self.end:]
        left = self.line[:self.start+1][::-1]    
        if left:
            try:
                self.start = self.start - last.search(left).start()
            except:
                pass
        if right:
            try:
                self.end += first.search(right).start() + 1
            except:
                pass

    def highlight(self):
        """
        Creates a string with highlighted words in search query
        """
        highlighted = self.line[self.start:self.end]
        for pos in self.position[::-1]:
            end = pos.end - self.start
            start = pos.start - self.start
            highlighted = highlighted[:end] + '</strong>' + highlighted[end:]
            highlighted = highlighted[:start] + '<strong>' + highlighted[start:]
        return highlighted
        
    def __eq__(self, wnd):
        """
        Check if two context windows are equal

        @param wnd: context window to check
        """
        return ((self.position == wnd.position) and
                (self.line == wnd.line) and
                (self.start == wnd.start) and
                (self.end == wnd.end))

    def __repr__(self):
        """
        Represents ContextWindow instance to string
        """
        return str(self.position)+ ', ' + str(self.start)+ ', ' \
               + str(self.end)+ ', ' + self.line

