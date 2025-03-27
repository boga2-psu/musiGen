from interp import Add, Sub, Mul, Div, Neg, Lit, Let, Name, If, Or, And, Not, Eq, Lt, Assign, Read, Letfun, App, Seq, Show, Play, Melody, Append, Chorus, Repeat, Expr, run

from lark import Lark, Token, ParseTree, Transformer
from lark.exceptions import VisitError
from pathlib import Path

parser = Lark(Path('expr.lark').read_text(),start='expr', parser='earley',ambiguity='explicit')

# A stricter parser which will fail if the grammar is ambiguous
#parser = Lark(Path('expr.lark').read_text(),start='expr', parser='lalr',strict=True)

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

    def bool(self, args: tuple[Token]) -> Expr:
        value = args[0].value == "true"
        return Lit(value)

    def id(self, args: tuple[Token]) -> Expr:
        return Name(args[0].value)
    
    def assign(self, args: tuple[Token, Expr]) -> Expr:
        return Assign(args[0].value, args[1])
    
    def read(self, args: tuple) -> Expr:
        return Read()

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

    def seq(self, args: tuple[Expr, Expr]) -> Expr:
        return Seq(args[0], args[1])

    def show(self, args: tuple[Expr]) -> Expr:
        return Show(args[0])

    def parenthesized(self, args):
        return args[0]

    # Domain extensions
    def melody_item(self, args) -> tuple[str, Expr]:
        pitch = args[0].value  # e.g., "C", "D#", "R"
        if isinstance(args[1], Token):
            duration = Lit(int(args[1].value))
        else:
            duration = args[1]
        return (pitch, duration)

    def melody(self, args) -> Melody:
        # args is a list of melody_item tuples like [("C", 1), ("D", 3)]
        return Melody(tuple(args))

    def play(self, args) -> Play:
        return Play(args[0])

    def append(self, args: tuple[Expr, Expr]) -> Append:
        left, right = args
        return Append(left, right)

    def repeat(self, args: tuple[Token, Expr]) -> Repeat:
        melody = args[0]
        if isinstance(args[1], Token):
            count = Lit(int(args[1]))
        else:
            count = args[1]
        return Repeat(count, melody)
    
    def chorus(self, args) -> Chorus:
        return Chorus(args[0])

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

# def test_cases():
#     test_expressions = [
#         '2 + 2',
#         '2 * 2',
#         '2 -2',
#         '2 / 2',
#         'if 5 < 10 then 42 else 99',
#         'letfun a(b) = c in d := e end',
#         'let a = b in c := d end',
#         'let x = 5 in if x < 10 then x + 1 else x - 1 end',
#         'let x = 5 in x + 3 end',
#         'let a = show x in b end',
#         'letfun a(b) = c in show x end',
#         'a(show x)',
#         'show melody(A1, F1, G1)',
#         'show letfun a(b) = c in d end',
#         'show if a then b else c',
#         'show true',
#         'x := ! a',
#         'x := letfun a(b) = c in d end',
#         'x; a && b',
#         'melody(A3, F2) ++ melody(G1, C5)',
#         'melody(A5, G2, C1) @ 2',
#         'melody(A1, G3) ++ melody(G3, B2) @ 2',
#         '** melody(A1, B1, C1, G1, F1, D1)',
#         '<= melody(A1, G2, F1, C2, F1, D1) =>',
#         '<= melody(A1, G1) ++ melody(B1, C1) @ 2 =>',
#         '<= ** melody(B1, D2, A1, G2, A1, B3) =>'
#     ]

#     for expr in test_expressions:
#         parse_and_run(expr)
#         print("-" * 60)
    
# test_cases()

def driver():
    print("Welcome to the Cb (C Flat) interpretter. Type 'exit' to quit.")

    while True:
        try:
            uInput = input("> ")

            if uInput.lower() in {"exit", "quit"}:
                print("Shutting down...")
                break

            parse_and_run(uInput)

        except KeyboardInterrupt:
                print("Shutting down...")
                break

        except Exception:
            pass

driver()