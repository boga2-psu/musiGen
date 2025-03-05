from interp import Add, Sub, Mul, Div, Neg, Lit, Let, Name, If, Or, And, Not, Eq, Lt, Letfun, App, Melody, Append, Repeat, Expr, run

from lark import Lark, Token, ParseTree, Transformer
from lark.exceptions import VisitError
from pathlib import Path

parser = Lark(Path('expr.lark').read_text(),start='expr',ambiguity='explicit')

class ParseError(Exception): 
    pass

def parse(s:str) -> ParseTree:
    try:
        return parser.parse(s)
    except Exception as e:
        raise ParseError(e)

class AmbiguousParse(Exception):
    pass

class ToExpr(Transformer[Token, Expr]):
    '''Transforms a parse tree into an AST expression tree'''

    # Binary operators
    def add(self, args: tuple[Expr, Expr]) -> Expr:
        return Add(args[0], args[1])

    def sub(self, args: tuple[Expr, Expr]) -> Expr:
        return Sub(args[0], args[1])

    def mul(self, args: tuple[Expr, Expr]) -> Expr:
        return Mul(args[0], args[1])

    def div(self, args: tuple[Expr, Expr]) -> Expr:
        return Div(args[0], args[1])

    def eq(self, args: tuple[Expr, Expr]) -> Expr:
        return Eq(args[0], args[1])

    def lt(self, args: tuple[Expr, Expr]) -> Expr:
        return Lt(args[0], args[1])

    def or_expr(self, args: tuple[Expr, Expr]) -> Expr:
        return Or(args[0], args[1])

    def and_expr(self, args: tuple[Expr, Expr]) -> Expr:
        return And(args[0], args[1])

    # Unary operators
    def neg(self, args: tuple[Expr]) -> Expr:
        return Neg(args[0])

    def not_expr(self, args: tuple[Expr]) -> Expr:
        return Not(args[0])

    # Literals and identifiers
    def int(self, args: tuple[Token]) -> Expr:
        return Lit(int(args[0].value))

    def id(self, args: tuple[Token]) -> Expr:
        return Name(args[0].value)

    # Control structures
    def if_expr(self, args: tuple[Expr, Expr, Expr]) -> Expr:
        return If(args[0], args[1], args[2])

    # Let bindings and functions
    def let(self, args: tuple[Token, Expr, Expr]) -> Expr:
        return Let(args[0].value, args[1], args[2])

    def letfun(self, args: tuple[Token, Token, Expr, Expr]) -> Expr:
        return Letfun(args[0].value, args[1].value, args[2], args[3])

    def app(self, args: tuple[Expr, Expr]) -> Expr:
        return App(args[0], args[1])

    def parenthesized(self, args):
        return args[0]

    # Domain extensions
    def melody_item(self, args) -> tuple[str, int]:
        pitch = args[0].value  # e.g., "C", "D#", "R"
        duration = int(args[1].value)
        return (pitch, duration)

    def melody(self, args) -> Melody:
        # args is a list of melody_item tuples like [("C", 1), ("D", 3)]
        return Melody(tuple(args))

    def append(self, args: tuple[Expr, Expr]) -> Append:
        left, right = args
        return Append(left, right)

    def repeat(self, args: tuple[Token, Expr]) -> Repeat:
        count = Lit(int(args[0].value))
        melody = args[1]
        return Repeat(count, melody)

    #Ambiguity Marker
    def _ambig(self, _) -> Expr:
        raise AmbiguousParse()

def genAST(t:ParseTree) -> Expr:
    '''Applies the transformer to convert a parse tree into an AST'''
    # boilerplate to catch potential ambiguity error raised by transformer
    try:
        return ToExpr().transform(t)               
    except VisitError as e:
        if isinstance(e.orig_exc,AmbiguousParse):
            raise AmbiguousParse()
        else:
            raise e
        
def parse_and_run(s: str):
    try:
        t = parse(s)
        print("raw:", t)    
        print("pretty:")
        print(t.pretty())
        ast = genAST(t)
        print("raw AST:", repr(ast))  # use repr() to avoid str() pretty-printing
        run(ast)                      # pretty-prints and executes the AST
    except AmbiguousParse:
        print("ambiguous parse")                
    except ParseError as e:
        print("parse error:")
        print(e)
    except EOFError:
        exit

def test_cases():
    test_expressions = [
        '2 + 2',
        '2 * 2',
        '2 -2',
        '2 / 2',
        'let x = 5 in x + 3 end',
        'let x = 5 in if x < 2 then 10 else 20 end',
        'if 1 < 2 then 3 else 4',
        'letfun f(x) = x + 1 in f(5) end',
        'let x = 1 in let y = 1 in x == y end end',
        'repeat(2, append(melody D3, C2, append(melody G1, B2, melody D1, B1)))'
    ]

    for expr in test_expressions:
        parse_and_run(expr)
        print("-" * 60)
    

test_cases()