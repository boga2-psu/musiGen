# Week 2 Practice Exercises  Part A (due at noon, 1/20/25)
#
# Your task is to complete the missing parts of this file.
#
# The file test2a.py contains a test driver for all the python
# problems in this assignment.  You can run it just using
# python3 test2a.py
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
# SUBMISSION: When you're done modifying this file, submit it
# to the Canvas dropbox, without zipping or renaming the file.
# Do not submit any other files.  There's no need to put your
# name in the source code; Canvas will tell us which submission is yours.
# MAKE SURE TO CLICK THE SUBMIT BUTTON; the submission isn't registered
# until then.  You can resubmit as many times as you like up
# until the deadline; we'll only look at the last submission.

# Other guideslines are the same as for week 1's exercises. 

# Most of the problems here have to do with definition and manipulation
# of abstract syntax trees (ASTs) for a simple language of Boolean expressions.

from dataclasses import dataclass

# Initally we'll consider a language with four kinds of expressions.
# An Expr is either an Or node or an And node or a Not node or a Boolean Literal leaf.
type Expr = Or | And | Not | Lit

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

# Here's a sample boolean expression, corresponding to the 
# the following concrete expression in C++-like syntax:
# (!(!true || !false) && !true)

a : Expr = \
    And(Not(Or(Not(Lit(True)),
               Not(Lit(False)))),
        Not(Lit(True)))    

print(a)

# Going forward, we strongly suggest that you work with these trees using
# recursive functions and match statements (not OO methods).
# Here are some examples of that style.
# The first two are analogs of functions we wrote on binary trees in week1's exercies.

def size(e:Expr) -> int:
    '''Return number of nodes in expression tree e'''
    match e:
        case And(l,r) | Or(l,r):   # note that we can combine two cases if they bind the same variables 
            return size(l) + size(r) + 1
        case Not(s):
            return size(s) + 1
        case Lit(_):
            return 1
        
print(size(a))  # should print 9

def flipOrs(e:Expr) -> Expr:
    '''Return a copy of expression tree e in which the operands to every
       Or operator are swapped.'''
    match e:
        case And(l,r):
            return And(flipOrs(l),flipOrs(r))
        case Or(l,r):
            return Or(flipOrs(r),flipOrs(l))
        case Not(s): 
            return Not(flipOrs(s))
        case Lit(_):
            return e
        
print(flipOrs(a))  
        
# And here is a function to compute the _result_ of a given expression.
# This is our first (very tiny) interpreter!
# Notice that we simply pass on the job of interpreting the
# operators to the corresponding Python operators.

def eval(e:Expr) -> bool:
    """Return the value of boolean expression e"""
    match e:
        case And(l,r):
             return eval(l) and eval(r)
        case Or(l,r):
             return eval(l) or eval(r)
        case Not(s):
             return not eval(s)
        case Lit(b):
             return b
        
print(eval(a))  # should print False  
print(eval(flipOrs(a)))  # should print False

# Now here are some problems for you to do.

# Problem 1
#
# Implement a function countNots that returns the number of Not nodes in
# the input expression tree.

def countNots(e:Expr) -> int:
    '''Return the number of Not nodes in the input expression tree'''
# SOLUTION
    match e:
        case And(l,r) | Or(l,r):   # note that we can combine two cases if they bind the same variables 
            return countNots(l) + countNots(r) 
        case Not(s):
            return countNots(s) + 1
        case Lit(_):
            return 0
        
print(countNots(a))        

# Problem 2
#
# Implement a function removeFalses that returns a copy of the input expression tree
# with each (Lit False) changed to (Not(Lit True)).
# 
# Note that the result tree should evaluate to the same boolean value as the
# input tree. In some ways, this is a silly function (why would we want to make
# expressions bigger while still computing the same thing?!) but it is
# fundamentally similar to a large class of program transformations
# ("optimizations") that interpreters and compilers use to make programs
# run faster. 
#
# Again, you're **not modifying the input tree**, you're returning a **new** tree. 

def removeFalses(e:Expr) -> Expr:
# SOLUTION:
    match e:
        case And(l,r):
            return And(removeFalses(l),removeFalses(r))
        case Or(l,r):
            return Or(removeFalses(l),removeFalses(r))
        case Not(s):
            return Not(removeFalses(s))
        case Lit(b):
            return e if b else Not(Lit(True))
        
print(removeFalses(a))
print(eval(removeFalses(a)))  # should print False

# Problem 3  (OPTIONAL CHALLENGE)
#
# Reminder: you do NOT have to attempt this problem in order to get full
# credit for a "good faith attempt."  
# 
# Implement the removeNots function so that it returns a version of the input tree
# that: (a) has no NotNodes
#       (b) produces the same boolean value as the input tree
#           when passed to the evalB function
#       (c) has size(tree) - countNots(tree) nodes
# To do this, you should take advantage of the following laws about Boolean
# expressions to systematically eliminate NotNodes: 
#
# !true = false
# !false = true
# !!x = x
# !(x || y) = !x && !y
# !(x && y) = !x || !y
#
# For example:
#
#   input: true
#   output: true
#
#   input: !false
#   output: true
#
#   input: !!!false
#   output: true
#
#   input: !(!true || !false) && !false
#   output: (true && false) && true
#
#   input: !(!true && !(false || !!true))
#   output: true || (false || true)

# Note: To make the recursion work out nicely, you may find it useful to define
# one or more auxiliary functions.

# SOLUTION:

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

print(removeNots(a))
assert(size(removeNots(a)) == size(a) - countNots(a))
