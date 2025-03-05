# A simple interpreter for arithmetic expressions with let bindings
# now including integer division.

from dataclasses import dataclass

type Expr = Add | Sub | Mul | Div | Neg | Lit | Let | Name | Ifnz | Letfun | App

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
    inexpr: Expr
    def __str__(self) -> str:
        return f"let {self.name} = {self.defexpr} in {self.inexpr} end"

@dataclass
class Name():
    name:str
    def __str__(self) -> str:
        return self.name

# Since we have no Booleans, we test an integer value directly; Ifnz stands for "if not zero"
@dataclass
class Ifnz():
    cond: Expr
    thenexpr: Expr
    elseexpr: Expr
    def __str__(self) -> str:
        return f"(if {self.cond} != 0 then {self.thenexpr} else {self.elseexpr})"
    
@dataclass
class Letfun():
    name: str
    param: str
    bodyexpr: Expr
    inexpr: Expr
    def __str__(self) -> str:
        return f"letfun {self.name} ({self.param}) = {self.bodyexpr} in {self.inexpr} end"
    
@dataclass
class App():
    fun: Expr
    arg: Expr
    def __str__(self) -> str:
        return f"({self.fun} ({self.arg}))"

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

type Value = int | Closure

@dataclass
class Closure:
    param: str
    body: Expr
    env: Env[Value]

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
        case(Lit(i)):
                return i
        case Name(n):
            v = lookupEnv(n, env)
            if v is None:
                raise EvalError(f"unbound name {n}")
            return v
        case Let(n,d,i):  
            v = evalInEnv(env, d)
            newEnv = extendEnv(n, v, env)
            return evalInEnv(newEnv, i)
        case Ifnz(c,t,e):
            match evalInEnv(env,c):
                case 0:
                    return evalInEnv(env,e)
                case _:
                    return evalInEnv(env,t)
        case Letfun(n,p,b,i):
            c = Closure(p,b,env)
            newEnv = extendEnv(n,c,env)
            c.env = newEnv        
            return evalInEnv(newEnv,i)
        case App(f,a):
            fun = evalInEnv(env,f)
            arg = evalInEnv(env,a)
            match fun:
                case Closure(p,b,cenv):
                    newEnv = extendEnv(p,arg,cenv) 
                    return evalInEnv(newEnv,b)
                case _:
                    raise EvalError("application of non-function")

        
def run(e: Expr) -> None:
    print(f"running: {e}")
    try:
        i = eval(e)
        print(f"result: {i}")
    except EvalError as err:
        print(err)