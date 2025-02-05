from lark import Lark, ParseTree
from pathlib import Path

parser = Lark(Path('expr.lark').read_text(),start='expr',ambiguity='explicit')
# We could also specify the grammar directly as a string argument to Lark

class ParseError(Exception):
    pass

def parse(s:str) -> ParseTree:
    try:
        return parser.parse(s)
    except Exception as e:
        raise ParseError(e)

def driver():
    while True:
        try:
            s = input('expr: ')
            t = parse(s)
            print("raw:", t)    
            print("pretty:")
            print(t.pretty())
        except ParseError as e:
            print("parse error:")
            print(e)
        except EOFError:
            break

driver()

