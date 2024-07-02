from typing import List
import re

# Think of 'class Atf` as a blueprint
# we will use this class, and the functions it contains to create multiple
# 'Atf' instances, upon all of which we will be able to use the functions below.

# Essentially creating a 'class' is a great way to attatch state (the lines of the file, or any specific data)
# to actions (selecting certain parts of the file for statistical purposes)

# In practice, we will create one Atf class instance for every .atf file you need to analyze.
# This will happen in main.py

class Atf:
    # the __init__ function tells python how to create a new Atf.
    # in this case, new Atfs will be created by providing a file path.
    # the Atf class instance will then read in the file and prepare it for
    # operations.
    
    # when reading this, remember that 'class Atf' is a blueprint. you'll see the 'self' 
    # variable everywhere below, think of 'self' as a placeholder for one specific atf
    
    def __init__(self, path: str):
        self.path = path
        self.lines: List[List[str]] = []
        self.scheme: List[str] = []
        
        self.load()
        
    def load(self):
        with open(self.path, 'r', encoding='utf-8', errors='replace') as f:
            for ix, line in enumerate(f.readlines()):
                if ix < 2:
                    continue
                
                if ix == 2:
                    self.build_scheme(line)
                    continue
                
                parts = re.split(r'\s+', line)
                self.lines.append(parts)
                
    def build_scheme(self, header: str):
        parts = header.split("\"")
        parts = [ re.sub(r'\s+', " ", field) for field in parts ]
        parts = [ part for part in parts if part != " "]
        self.scheme = parts
        
    def grab_by_name(self, key: str):
        ix = self.scheme.index(key)
        return [ row[ix] for row in self.lines ]
    
    def grab_by_order(self, ix: int):
        return [ row[ix] for row in self.lines ]
            