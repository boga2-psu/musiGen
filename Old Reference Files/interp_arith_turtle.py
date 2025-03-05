# A simple interpreter for arithmetic expressions with let bindings
# now including domain-specific extensions for turtle grpahics paths.
# Note: to execute this, you'll need a version of python that has tk
# already built-in; you can't just download a package.

from dataclasses import dataclass

# Define primitive turtle path literals
type Action = Forward | Left

@dataclass
class Forward():
    distance: int
    def __str__(self) -> str:
        return f"Forward({self.distance})"
    
@dataclass
class Left():
    angle: int
    def __str__(self) -> str:
        return f"Left({self.angle})"

type Literal = int | Action

type Expr = Add | Sub | Mul | Div | Neg | Lit | Let | Name | Append | Repeat

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
    value: Literal
    def __str__(self) -> str:
        return f"{self.value}"
    
@dataclass
class Append():
    left: Expr
    right: Expr
    def __str__(self) -> str:
        return f"({self.left} ++ {self.right})"
    
@dataclass
class Repeat():
    count: Expr
    path: Expr
    def __str__(self) -> str:
        return f"({self.count} @ {self.path})"    


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

b : Expr = Let('x', Lit(1), 
                    Let('x', Lit(2), 
                             Mul(Name('x'), Lit(3))))

c : Expr = Add(Let('x', Lit(1), 
                        Sub(Name('x'), Lit(2))),
               Mul(Name('x'), Lit(3)))

d : Expr = Add(Lit(1), Div(Lit(2), Lit(0)))

box : Expr = Let("side", Lit(Forward(100)), 
                 Repeat(Lit(4), 
                        Append(Name("side"), 
                               Lit(Left(90)))))
star: Expr = Repeat(Lit(36), Append(Lit(Forward(200)), Lit(Left(170))))

type Binding[V] = tuple[str,V]  # this tuple type is always a pair
type Env[V] = tuple[Binding[V], ...] # this tuple type has arbitrary length 

from typing import Any
emptyEnv : Env[Any] = ()  # the empty environment has no bindings

def extendEnv[V](name: str, value: V, env:Env[V]) -> Env[V]:
    '''Return a new environment that extends the input environment env with a new binding from name to value'''
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

@dataclass
class Path:
    p: tuple[Action, ...]

type Value = int | Path

def eval(e: Expr) -> Value :
    return evalInEnv(emptyEnv, e)

def evalInEnv(env: Env[Value], e:Expr) -> Value:
    match e:
        case Add(l,r):
            match (evalInEnv(env,l), evalInEnv(env,r)):
                case (int(lv), int(rv)):
                    return lv + rv
                case _:
                    raise EvalError("addition of non-integers")
        case Sub(l,r):
            match (evalInEnv(env,l), evalInEnv(env,r)):
                case (int(lv), int(rv)):
                    return lv - rv
                case _:
                    raise EvalError("subtraction of non-integers")
        case Mul(l,r):
            match (evalInEnv(env,l), evalInEnv(env,r)):
                case (int(lv), int(rv)):
                    return lv * rv
                case _:
                    raise EvalError("multiplication of non-integers")
        case Div(l,r):
            match (evalInEnv(env,l), evalInEnv(env,r)):
                case (int(lv), int(rv)):
                    if rv == 0:
                        raise EvalError("division by zero")
                    return lv // rv
                case _:
                    raise EvalError("division of non-integers")                
        case Neg(s):
            match evalInEnv(env,s):
                case int(i):
                    return -i
                case _:
                    raise EvalError("negation of non-integer")
        case(Lit(lit)):
            match lit:  # two-level matching keeps type-checker happy
                case int(i):
                    return i
                case Forward(_) as a:
                    return Path((a,))
                case Left(_) as a:
                    return Path((a,))
        case Append(l,r):
            match (evalInEnv(env,l), evalInEnv(env,r)):
                case (Path(pl), Path(pr)):
                    return Path(pl + pr)
                case _:
                    raise EvalError("append of non-paths")
        case Repeat(c,p):   
            match (evalInEnv(env,c), evalInEnv(env,p)):
                case (int(i),Path(pl)):
                    return Path(pl * i)
                case _:
                    raise EvalError("repeat of non-path")
        case Name(n):
            v = lookupEnv(n, env)
            if v is None:
                raise EvalError(f"unbound name {n}")
            return v
        case Let(n,d,b):
            v = evalInEnv(env, d)
            newEnv = extendEnv(n, v, env)
            return evalInEnv(newEnv, b)
        
        
import turtle as t
import time

def run(e: Expr) -> None:
    print(f"running {e}")
    try:
        match eval(e):
            case int(i):
                print(f"result: {i}")
            case Path(path):
                t.clearscreen()
                t.speed(8)
                for a in path:
                    match a:
                        case Forward(d):
                            t.forward(d)
                        case Left(a):
                            t.left(a)
                time.sleep(5)
    except EvalError as err:
        print(err)

run(a)
run(b)
run(c)
run(d)

run(box)
run(star)
t.mainloop()

