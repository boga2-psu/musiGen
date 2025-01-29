# Week 2 Practice Exercises Part B (due at noon, 1/20/25)
#
# Your task is to complete the missing parts of this file.
#
# The file test2b.py contains a test driver for all the python
# problems in this assignment.  You can run it just using
# python3 test2b.py
# Of course, you may wish to do additional testing as well.
#
# You will receive credit for each problem you ATTEMPT, even
# if your code does not work perfectly. Make sure that
# your submitted file can be executed by Python, i.e.
# don't let errors in incomplete solutions prevent your
# completed code from running!
#
# If a problem is marked OPTIONAL CHALLENGE, that means it is a bit
# more difficult than the others, and you are NOT required to attempt
# it in order to get full credit for a "good faith effort" on this file.
#
# SUBMISSION: When you're done modifying this file, zip it
# with the other required files according to README.txt instructions
# and submit it to the Canvas dropbox. There's no need to put your
# name in the source code; Canvas will tell us which submission is yours.
# MAKE SURE TO CLICK THE SUBMIT BUTTON; the submission isn't registered
# until then.  You can resubmit as many times as you like up
# until the deadline; we'll only look at the last submission.

# Other guideslines are the same as for week 1's exercises. 

# Most of the problems here have to do with definition and manipulation
# of abstract syntax trees (ASTs) for a simple language of Boolean expressions.

from dataclasses import dataclass

# In this file, we'll extend our Boolean expression language with variables.

# We're adding in two brand new features this time: our expression tree type has a new
# type of node that represents a **let binding** and a new type of leaf
# that represents a **variable name**. This means our Boolean expressions can
# now contain definitions and uses of variable names, and when we interpret an
# expression to calculate its value, we'll have to keep track of the values of
# defined variables in order to provide values for any names in the expression.

# Our new Expr type for abstract syntax trees looks just like our Expr type
# from exercises2a, except with two extra cases for Let nodes and Name leaves.

type Expr = Or | And | Not | Lit | Let | Name

# The first four types are unchanged:

@dataclass
class Or():
    left: Expr
    right: Expr
    def __str__(self) -> str:
        return f"({self.left} or {self.right})"

@dataclass
class And():
    left: Expr
    right: Expr
    def __str__(self) -> str:
        return f"({self.left} and {self.right})"

@dataclass
class Not():
    subexpr: Expr
    def __str__(self) -> str:
        return f"(not {self.subexpr})"

@dataclass
class Lit():
    value: bool
    def __str__(self) -> str:
        return f"{self.value}"

# The Let node type is new for this file: it carries the name of
# the variable being defined, and two subtrees, one for the
# defining expression and one for the body over which the
# definition is in scope.

@dataclass
class Let():
    name: str
    defexpr: Expr
    bodyexpr: Expr
    def __str__(self) -> str:
        return f"(let {self.name} = {self.defexpr} in {self.bodyexpr})"

# The Name type is also new in this file: it represents a **use** of a
# variable in an expression.

@dataclass
class Name():
    name:str
    def __str__(self) -> str:
        return self.name
    
# Here's an example tree using these new features
# corresponding to the concrete expression
# let y = x || true in not y

b : Expr = \
    Let('y',Or(Name('x'),Lit(True)),
        Not(Name('y')))

print(b)

# Since this expression language is a superset of
# the one in the week2a, the expressions we used
# there are still valid, e.g.  

a : Expr = \
   And(Not(Or(Not(Lit(True)),
              Not(Lit(False)))),
       Not(Lit(True)))    

print(a)

# Now here are some problems for you to do.

# Problem 4
#
# Implement a function countNameOccurrences that, given a name,
# returns the number of Name leaves in the tree containing that name.
# For example:

#   name: "x"
#   tree: !true || false
#   output: 0

#   name: "x"
#   tree: x && true
#   output: 1

#   name: "x"
#   tree: !(x && x) || y
#   output: 2

#   name: "x"
#   tree: let x = true in !x
#   output: 1

#   name: "x"
#   tree: let y = x in !y
#   output: 1

# You may be tempted to convert the input Expr into a string, and then
# using library functions to search that string, but you must **NOT** do this!
# It is theoretically possible to solve this problem
# that way, but that's not the exercise that we're aiming for here.

# SOLUTION:

def countNameOccurrences(n:str, e:Expr) -> int:
    '''Return the number of (Name n) nodes in the input expression tree'''
    match e:
        case And(l,r) | Or(l,r):   # note that we can combine two cases if they bind the same variables 
            return countNameOccurrences(n,l) + countNameOccurrences(n,r) 
        case Not(s):
            return countNameOccurrences(n,s)
        case Lit(_):
            return 0
        case Let(_,d,b):
            return countNameOccurrences(n,d) + countNameOccurrences(n,b)
        case Name(n0):
            return 1 if n == n0 else 0  # could just write n == n0, since in Python True == 1 and False == 0

print(countNameOccurrences("x",b))  # should print 1

# ************
# ENVIRONMENTS
# ************


# When we interpret an expression that contains variables, how do we know what
# value each variable should have?

# Our interpreter function needs a way to **map** variable names to variable
# values, in this case Booleans. In PL terminology, we need a **binding** for
# each variable in our program: a known definition that says what the exact
# value of the variable is.

# An **environment** is fundamentally a collection of variable **bindings**.
# We will represent environments as an explicit **tuple** of bindings.
# (Recall that a tuple is just an immutable list.)
# The order of this tuple is somewhat important, as we will see later.
# (It might seem more natural to represent environments using Python dictionaries,
# but we have our reasons!)

type Binding[V] = tuple[str,V]  # this tuple type is always a pair
type Env[V] = tuple[Binding[V], ...] # this tuple type has arbitrary length 

# We will want several different kinds of enviroment mappings, each indexed
# by variables names, but mapping these to different types of values (bools,
# Exprs, etc.) Therefore, we make the type of values a *parameter* V of the
# Binding and Env definitions.

from typing import Any
emptyEnv : Env[Any] = ()  # the empty environment has no bindings

# The (only) way we create new environments is by **extending** an existing
# environment with a new binding. 

def extendEnv[V](name: str, value: V, env:Env[V]) -> Env[V]:
    '''Return a new environment that extends the input environment env with a new binding from name to value'''
    return ((name,value),) + env

# Here is an example that shows how we might create an environment
# using a series of extensions. In practice, we will never need to create
# stand-alone environments like this, except perhaps for testing, but
# you may find it useful to walk through this function in the debugger
# to see how it works.

def sampleBoolEnv() -> Env[bool] :
    env1 : Env[bool] = extendEnv('x', True, emptyEnv)  # type annotations help keep typechecker happy
    env2 : Env[bool] = extendEnv('y', False, env1)
    env3 : Env[bool] = extendEnv('x', False, env2)
    # Notice that this environment has **two** bindings for 'x'.
    # In such cases, only the **last* binding added, which is the
    # **first** binding in the list, will be used. 
    # This will become clearer below.
    return env3

# For input and display purposes, we write an environment as a 
# comma-separated list of (key,value) pairs, with extension occuring
# at the left. For example, the result of sampleBoolEnv() defined above 
# will display as
# (('x',False),('y',False),('x',True))

print(sampleBoolEnv())

# The other operation we need on environments is a way of doing **lookup**
# on a name to discover its corresponding value.  Such a lookup might fail,
# if there is no binding for that name; for now we'll just throw a
# Python exception if this happens. 

# It's good practice to define a new custom exception type for each different
# kind of exception we plan to throw. We make it a subclass of the builtin
# Exception class
class EnvError(Exception):
    pass

# This function is our only interface for using the Env type, for now.
# Notice that we return the value for the **first** matching binding.
# Since environments are extended by adding bindings onto the front,
# this means we return the value used with the **most recent** extension
# made for this variable.
def lookupEnv[V](name: str, env: Env[V]) -> V :
    '''Return the first value bound to name in the input environment env
       (or raise an exception if there is no such binding)'''
    try:
        return next(v for (n,v) in env if n == name)   # use handy generator expression to search for name
    except StopIteration:
        raise EnvError('name is not in environment: ' + name)        

print(lookupEnv('x',sampleBoolEnv()))  # should print False
# print(lookupEnv('z',sampleBoolEnv()))  # should raise EnvError

# Problem 5 

# Write a function uniquifyEnv() that removes any duplicate bindings for the
# same name, leaving just the first (i.e. most recent) one. 

# For example (with V=bool):

#   input: (("a", True), ("b", False), ("a", False), ("c",True))
#   output: (("a", True), ("b", False), ("c", True))

# Note that for any n and env, we should have
# lookupEnv[V](n,env) = lookupEnv[V](n,unquifyEnv[V](env))

# Hint: you may find it useful to use a helper function.
# Also, depending on the approach you take, you may have trouble
# getting your code to pass  the type checker.

# SOLUTION:

def uniquifyEnv[V](env: Env[V]) -> Env[V] :
    """Return a copy of the input environment with all duplicate name bindings removed"""
    match env:
        case ((n,v),*env1):
            return ((n,v),) + uniquifyEnv(tuple((n0,v0) for (n0,v0) in env1 if n0 != n))
        case _: return ()

print(uniquifyEnv(sampleBoolEnv()))  # should print (('x', False), ('y', False))

# An alternative solution   
def uniquifyEnv1[V](env: Env[V],seen:set[str] = set()) -> Env[V] :
    match env:
        case ((n,v),*env1):
            if n in seen:
                return uniquifyEnv1(env1, seen) # type: ignore
            else:
                return ((n,v),) + uniquifyEnv1(env1, seen | {n}) # type: ignore
        case _: return ()

print(uniquifyEnv1(sampleBoolEnv()))  # should print (('x', False), ('y', False))


# EVALUATION WITH ENVIRONMENTS

# Now when we want to interpret an expression to find its value, we can take
# in an environment to tell our interpreter what the value of each variable should be. 

# To evaluate an entire top-level expression, we set env to be emptyEnv.

def eval(e: Expr) -> bool :
    return evalInEnv(emptyEnv, e)

def evalInEnv(env: Env[bool], e:Expr) -> bool:
    match e:
        # Most of the cases are just as in our previous evaluator,
        # except that we must pass the environment value to
        # the next recursive call, so that it's available at every level of the
        # recursion.
        case And(l,r):
             return evalInEnv(env,l) and evalInEnv(env,r)
        case Or(l,r):
             return evalInEnv(env,l) or evalInEnv(env,r)
        case Not(s):
             return not evalInEnv(env,s)
        case Lit(b):
             return b
        # Finally, the interesting new cases.
      
        # When we see a Name leaf, we look up the value of that name in the environment.
        case Name(n):
             return lookupEnv(n,env)

        # If the root of the tree is a LetNode, we
        # (i) evaluate the definition subtree to a value (using the original environment);
        # (ii) build an extended environment that maps the let-bound
        #    variable to that value
        # (iii) evaluate the body subtree in the extended enviroment.
        case Let(n,d,b):
          v = evalInEnv(env, d)
          newEnv = extendEnv(n, v, env)
          return evalInEnv(newEnv, b)
        
# Problem 6

# Implement the substituteAllNames function so that it replaces each Name leaf
# with a Lit leaf carrying the value from the corresponding binding in the given
# environment. For example:

#   environment: x = True, y = False
#   expr: x || false
#   output: true || false

#   environment: x = True, y = False
#   expr: x || y
#   output: true || false

#   environment: x = True, y = False
#   expr: !x && !(y || x)
#   output: !true && !(false || true)

#   environment: x = True, y = False
#   expr: let x = !y in y
#   output: let x = !false in false

#   environment: x = True, y = False
#   expr: let x = false in x
#   output: let x = false in true

# You may assume that all variables in the tree have bindings in the environment, so
# the lookup function will never throw a EnvError. 

# You should use the lookupEnv() function to access the environment. Read the comments
# in this file to learn how to use the Env type!

# TROUBLE ALERT!
# As specified, this function is *NOT* faithful to the intended semantics of our
# language, in the following sense: there are environnments env and expressions e such that
# interpret(env,e) != interpret(env,substituteAllNames(env,e)).
# Include a comment in your code giving an example of an env and t that could cause this
# problem, and explaining why the problem occurs.  

# SOLUTION:

def substituteAllNames(env: Env[bool], e:Expr) -> Expr:
    '''Return copy of e in which all Name leaves have been replaced by Lit leaves
       carrying the value from the corresponding binding in the given environment''' 
    match e:
        case And(l,r):
            return And(substituteAllNames(env,l),substituteAllNames(env,r))
        case Or(l,r):
            return Or(substituteAllNames(env,l),substituteAllNames(env,r))
        case Not(s):
            return Not(substituteAllNames(env,s))
        case Lit(_):
            return e
        case Name(n):
            return Lit(lookupEnv(n,env))
        case Let(n,d,b):
            return Let(n,substituteAllNames(env,d),substituteAllNames(env,b))
        # The last example in the header comment illustrates the problem:
        # when we descend beneath a Let node that rebinds a variable already
        # in the environment, the interpreter updates the environment to
        # reflect the inner binding, but this function does not. 


# Problem 7 

# Implement the function simplifyBindings, which maps expression trees to *simplified* expression trees that have 
# no Let nodes or Name leafs, by replacing each Name leaf with the (simplification of) the defExpr
# of the corresponding Let node.

# For example:

#   input: let x = true in 
#            let y = x in
#              !y 
#   output: !true 

#   input: let x = true in 
#            let x = false in 
#              !x 
#   output: !false

#   input: false && (let x = true in x) 
#   output: false && true 

#   input: let x = true || false in
#            x && true
#   output: (true || false) && true

# Again, you may assume that all variable uses in the input expression are in the scope of a binding, 
# so if you process Let nodes correctly, the lookup function will never throw a EnvError
# at a Name leaf. 

# A correct solution should have the property that
# eval(e) = eval(simplifyBindings(e)) for all expressions e.
# In other words, unlike the somewhat bogus substituteAllNames function above,
# simplifyExpr makes good semantic sense.

# To further structure the problem, we provide a definition of simplifyBindings in terms of
# a helper function simplifyInEnv, which carries an environment much as in the evalInEnv function.  
# However, unlike that function, here the environment maps names to (simplified) expression trees, rather
# than to bools. Again, to process a whole tree, we start with an empty environment.

# SOLUTION:

def simplifyBindings(e: Expr) -> Expr:
  return simplifyInEnv(emptyEnv, e)

def simplifyInEnv(env: Env[Expr], e: Expr) -> Expr:
    '''Return a copy of e in which all Name leaves have been replaced by the corresponding defExpr
       of the corresponding Let node, and all Let nodes have been removed'''  
    match e:
        case And(l,r):
            return And(simplifyInEnv(env,l), simplifyInEnv(env,r))  
        case Or(l,r):
            return Or(simplifyInEnv(env,l), simplifyInEnv(env,r))   
        case Not(s):    
            return Not(simplifyInEnv(env,s))
        case Lit(_):
            return e
        case Name(n):
            return lookupEnv(n, env)
        case Let(n, d, b):
            d0 = simplifyInEnv(env, d)
            newEnv = extendEnv(n, d0, env)
            return simplifyInEnv(newEnv, b)

print(simplifyBindings(Let("x", Lit(True), Let("y", Name("x"), Not(Name("x"))))))  # should print (not True)

# Problem 8 (OPTIONAL CHALLENGE)
#
# Reminder: you do NOT have to attempt this problem in order to get full
# credit for a "good faith attempt."  
#
# Write a function simplifyToBool that simplifies an arbitrary expression tree e to a single Lit leaf, such that
# interp(e) = interp(simplifyToBool(e)) for any expression e.

# There are several good approaches to this problem.
# You may find inspiration in (or make direct use of) the simplifyBindings
# function above and the removeNots function from exercises2a.py.

# As usual, you may assume that each variable use in the input expression is in the scope
# of a Let binding for that variable. 

# SOLUTION 1

# There are several ways to attack this problem.

# One appraoch is to recognize that we have already done most of the
# work in the simplifyBindings function of the previous problem, 
# which gets rid of Lets and Names,
# and in the removeNots function from exercises2a.py, which gets rid of Nots.
# All that's left are Ands and Ors over Lits.  So we can write
# function to handle those cases, and then glue everything together.

def simplifyToBool1(e:Expr) -> Lit: 
  # remove Let nodes and Name leaves
  e = simplifyBindings(e)
  # remove Not nodes
  e = removeNots(e)
  # handle And and Or nodes
  return simplifyAndOr(e)

# Note: does not handle Let, Name, and Not because
# it expects those cases to have already been removed.
def simplifyAndOr(e:Expr) -> Lit:
      match e:
        case Lit(_):
            return e
        case And(l,r):
            return Lit(simplifyAndOr(l).value and simplifyAndOr(r).value)
        case Or(l,r):
            return Lit(simplifyAndOr(l).value or simplifyAndOr(r).value)
        case _:
           # this default case should never occur if the input is well-formed
           assert(False)


# Copied from exercises2a.py
# (Can't just import this, because definition of Expr is different)
# Again, no need to handle Let or Name, because we assume they have been removed.
def removeNots(e:Expr) -> Expr: 
    """Return a copy of e with all Not nodes replaced by logically equivalent expression"""
    match e:
        case Or(l,r):
            return Or(removeNots(l),removeNots(r))
        case And(l,r):
            return And(removeNots(l),removeNots(r))
        case Not(s):
            return removeNotsNeg(s)
        case Lit(_):
            return e
        case _:
            assert(False)

def removeNotsNeg(e:Expr) -> Expr: 
    match e:
        case Or(l,r):
            return And(removeNotsNeg(l),removeNotsNeg(r))
        case And(l,r):
            return Or(removeNotsNeg(l),removeNotsNeg(r))
        case Not(s):
            return removeNots(s)
        case Lit(b):
             return Lit(not b)
        case _:
            return e


# SOLUTION 2 

# Another approach is to write a single recursive traversal that
# relies on the fact that subtrees are always reduced to BoolLeafs
# by the recursive calls. Then each case just has to deal with
# those BoolLeaf values, which is really just like dealing with
# boolean values in the interpreter -- so we can just copy
# the structure of eval.

def simplifyToBool2 (e: Expr) -> Lit:
    return simplifyToBoolInEnv(emptyEnv,e)

def simplifyToBoolInEnv(env: Env[Lit], e: Expr) -> Lit:
    match e:
        case Or(l,r):
            litl = simplifyToBoolInEnv(env, l)
            litr = simplifyToBoolInEnv(env, r)
            return Lit(litl.value or litr.value)
        case And(l,r):
            litl = simplifyToBoolInEnv(env, l)
            litr = simplifyToBoolInEnv(env, r)
            return Lit(litl.value and litr.value)
        case Not(s):
            lits = simplifyToBoolInEnv(env, s)
            return Lit(not lits.value)
        case Name(n):
            return lookupEnv(n, env)
        case Let(n,d,b):
            litd = simplifyToBoolInEnv(env, d)
            newEnv = extendEnv(n, litd, env)
            return simplifyToBoolInEnv(newEnv, b)
        case Lit(b):
            return e

# SOLUTION 3
# 
# The easiest solution -- though it admittedly doesn't give you much
# additional Python coding experience -- is to realize that
# we can simply use the existing interpreter itself and plug
# the resulting boolean value back into a Bool leaf:

def simplifyToBool3(e: Expr) -> Lit:
    return Lit(eval(e))

