# A simple interpreter for arithmetic expressions with let bindings
# now including integer division.

from dataclasses import dataclass

type Expr = Add | Sub | Mul | Div | Neg | Lit | Let | Name

@dataclass
class Add():
    left: Expr
    right: Expr
    def __str__(self) -> str:
        return f"({self.left} + {self.right})"

@dataclass
class Sub():
    left: Expr
    right: Expr
    def __str__(self) -> str:
        return f"({self.left} - {self.right})"

@dataclass
class Mul():
    left: Expr
    right: Expr
    def __str__(self) -> str:
        return f"({self.left} * {self.right})"

@dataclass
class Div():
    left: Expr
    right: Expr
    def __str__(self) -> str:
        return f"({self.left} / {self.right})"

@dataclass
class Neg():
    subexpr: Expr
    def __str__(self) -> str:
        return f"(- {self.subexpr})"

@dataclass
class Lit():
    value: int
    def __str__(self) -> str:
        return f"{self.value}"

@dataclass
class Let():
    name: str
    defexpr: Expr
    bodyexpr: Expr
    def __str__(self) -> str:
        return f"(let {self.name} = {self.defexpr} in {self.bodyexpr})"

@dataclass
class Name():
    name:str
    def __str__(self) -> str:
        return self.name

a : Expr = Let('x', Add(Lit(1), Lit(2)), 
                    Sub(Name('x'), Lit(3)))
print(a)

b : Expr = Let('x', Lit(1), 
                    Let('x', Lit(2), 
                             Mul(Name('x'), Lit(3))))
print(b)  

c : Expr = Add(Let('x', Lit(1), 
                        Sub(Name('x'), Lit(2))),
               Mul(Name('x'), Lit(3)))
print(c)

d : Expr = Add(Lit(1), Div(Lit(2), Lit(0)))
print(d)

type Binding[V] = tuple[str,V]  # this tuple type is always a pair
type Env[V] = tuple[Binding[V], ...] # this tuple type has arbitrary length 

from typing import Any
emptyEnv : Env[Any] = ()  # the empty environment has no bindings

def extendEnv[V](name: str, value: V, env:Env[V]) -> Env[V]:
    '''Return a new environment that extends the input environment 
       env with a new binding from name to value'''
    return ((name,value),) + env

def lookupEnv[V](name: str, env: Env[V]) -> (V | None) :
    '''Return the first value bound to name in the input environment env
       (or raise an exception if there is no such binding)'''
    # exercises2b.py shows a different implementation alternative
    match env:
        case ((n,v), *rest) :
            if n == name:
                return v
            else:
                return lookupEnv(name, rest) # type:ignore
        case _ :
            return None        
        
class EvalError(Exception):
    pass

def eval(e: Expr) -> int :
    return evalInEnv(emptyEnv, e)

def evalInEnv(env: Env[int], e:Expr) -> int:
    match e:
        case Add(l,r):
            return evalInEnv(env,l) + evalInEnv(env,r)
        case Sub(l,r):
            return evalInEnv(env,l) - evalInEnv(env,r)
        case Mul(l,r):
            lv = evalInEnv(env,l)
            rv = evalInEnv(env,r)
            return lv * rv
        case Div(l,r):
            lv = evalInEnv(env,l)
            rv = evalInEnv(env,r)
            if rv == 0:
                raise EvalError("division by zero")
            return lv // rv
        case Neg(s):
            return - (evalInEnv(env,s))
        case Lit(i):
            return i
        case Name(n):
            v = lookupEnv(n, env)
            if v is None:
                raise EvalError(f"unbound name {n}")
            return v
        case Let(n,d,b):
            v = evalInEnv(env, d)
            newEnv = extendEnv(n, v, env)
            return evalInEnv(newEnv, b)
        
def run(e: Expr) -> None:
    print(f"running: {e}")
    try:
        i = eval(e)
        print(f"result: {i}")
    except EvalError as err:
        print(err)

run(a)
run(b)
run(c)
run(d)


