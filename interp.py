''' 
Milestone 1 Fixes
-----------------

Arithmetic/booleans/lets implemented correctly  9/20 points --
    - Arithmetic operators now throw errors when
      given boolean arguments

    - eval() method now has the correct signature
      and now only accepts an expression as an 
      argument i.e. eval(e)

Lt implemented correctly -- 2.5/5 points
    - Now throws an error when given 
      boolean arguments

Evaluation of new operators -- 5/10 points
    - Repeat and append operators now work

run() does something with custom value types -- 5/10 points
    - run() now populates the midi file with note
      data and opens your defualt media player to
      attempt to play the resulting file

'''

from midiutil import MIDIFile
from dataclasses import dataclass
from typing import Any
import os

type Expr = Add | Sub | Mul | Div | Neg | Lit | Let | Name | If | Or | And | Not | Eq | Lt | Letfun | App | Melody | Append | Repeat
type Literal = int | bool

#____________________________________________________________________________________________________________________________
#
# Types & Definitions
#____________________________________________________________________________________________________________________________

@dataclass
class Add:
    left: Expr
    right: Expr

    def __str__(self) -> str:
        return f"({self.left} + {self.right})"

@dataclass
class Sub:
    left: Expr
    right: Expr

    def __str__(self) -> str:
        return f"({self.left} - {self.right})"

@dataclass
class Mul:
    left: Expr
    right: Expr

    def __str__(self) -> str:
        return f"({self.left} * {self.right})"

@dataclass
class Div:
    left: Expr
    right: Expr

    def __str__(self) -> str:
        return f"({self.left} / {self.right})"

@dataclass
class Neg:
    subexpr: Expr

    def __str__(self) -> str:
        return f"(- {self.subexpr})"

@dataclass
class Lit:
    value: Literal

    def __str__(self) -> str:
        return f"{self.value}"
    
@dataclass
class Let:
    name: str
    defexpr: Expr
    bodyexpr: Expr

    def __str__(self) -> str:
        return f"(let {self.name} = {self.defexpr} in {self.bodyexpr})"

@dataclass
class Name:
    name:str

    def __str__(self) -> str:
        return self.name
    
@dataclass
class If:
    cond: Expr
    t_branch: Expr
    e_branch: Expr

    def __str__(self) -> str:
        return f"(if {self.cond} then {self.t_branch} else {self.e_branch})"

        
@dataclass
class Or:
    left: Expr
    right: Expr
    def __str__(self) -> str:

        return f"({self.left} or {self.right})"

@dataclass
class And:
    left: Expr
    right: Expr

    def __str__(self) -> str:
        return f"({self.left} and {self.right})"

@dataclass
class Not:
    subexpr: Expr

    def __str__(self) -> str:
        return f"(not {self.subexpr})"
    
@dataclass
class Eq:
    left: Expr
    right: Expr

    def __str__(self) -> str:
        return f"({self.left} == {self.right})"

@dataclass
class Lt:
    left: Expr
    right: Expr

    def __str__(self) -> str:
        return f"({self.left} < {self.right})"

@dataclass
class Letfun:
    name: str
    param: str
    bodyexpr: Expr
    inexpr: Expr
    def __str__(self) -> str:
        return f"letfun {self.name} ({self.param}) = {self.bodyexpr} in {self.inexpr} end"
    
@dataclass
class App:
    fun: Expr
    arg: Expr
    def __str__(self) -> str:
        return f"({self.fun} ({self.arg}))"

@dataclass
class Melody:
    notes: tuple[tuple[str, int], ...]  # Tuple of (pitch, duration) pairs

    def __str__(self) -> str:
        note_strs = [f"{pitch}{duration}" for pitch, duration in self.notes]
        return "[" + " ".join(note_strs) + "]"
    
@dataclass
class Append:
    left: Expr
    right: Expr

    def __str__(self) -> str:
        return f"(append {self.left} {self.right})"
    
@dataclass
class Repeat:
    count: Expr
    melody: Expr

    def __str__(self) -> str:
        return f"(repeat {self.count} {self.melody})"
    

#____________________________________________________________________________________________________________________________
#
# Environment & Compiler
#____________________________________________________________________________________________________________________________

type Binding[V] = tuple[str,V]  # A pair of name and value
type Env[V] = tuple[Binding[V], ...] # An environment is a tuple of bindings

type Value = int | bool | Melody | Closure
@dataclass
class Closure:
    param: str
    body: Expr
    env: Env[Value]

emptyEnv : Env[Any] = ()  # The empty environment has no bindings

def extendEnv[V](name: str, value: V, env:Env[V]) -> Env[V]:
    '''Extend environment with a new variable.'''
    return ((name,value),) + env

def lookupEnv[V](name: str, env: Env[V]) -> V | None:
    """Look up a variable in the environment."""
    for n, v in env:
        if n == name:
            return v
    return None     
        
class EvalError(Exception):
    pass


def eval(e: Expr) -> Value :
    return evalInEnv(emptyEnv, e)

def evalInEnv(env: Env[Value], e:Expr) -> Value:
    match e:
        # Arithmetic Evals
        # ______________________________________________
        case Add(l,r):
            match (evalInEnv(env,l), evalInEnv(env,r)):
                case (int(lv), int(rv)) if not isinstance(lv, bool) and not isinstance(rv, bool):
                    return lv + rv
                case _:
                    raise EvalError("addition of non-integers")
                
        case Sub(l,r):
            match (evalInEnv(env,l), evalInEnv(env,r)):
                case (int(lv), int(rv)) if not isinstance(lv, bool) and not isinstance(rv, bool):
                    return lv - rv
                case _:
                    raise EvalError("subtraction of non-integers")
                
        case Mul(l,r):
            match (evalInEnv(env,l), evalInEnv(env,r)):
                case (int(lv), int(rv)) if not isinstance(lv, bool) and not isinstance(rv, bool):
                    return lv * rv
                case _:
                    raise EvalError("multiplication of non-integers")
                
        case Div(l,r):
            match (evalInEnv(env,l), evalInEnv(env,r)):
                case (int(lv), int(rv)) if not isinstance(lv, bool) and not isinstance(rv, bool):
                    if rv == 0:
                        raise EvalError("division by zero")
                    return lv // rv
                case _:
                    raise EvalError("division of non-integers")
                                
        case Neg(s):
            match evalInEnv(env,s):
                case int(i) if not isinstance(i, bool):
                    return -i
                case _:
                    raise EvalError("negation of non-integer")
                
        case Lt(l, r):
            match (evalInEnv(env, l), evalInEnv(env, r)):
                case (int(lv), int(rv)) if not isinstance(lv, bool) and not isinstance(rv, bool):
                    return lv < rv
                case _:
                    raise EvalError("< requires integer operands")
                
        # Variable Evals
        # ______________________________________________                
        case(Lit(i)):
                return i
        
        case Let(n,d,i):  
            v = evalInEnv(env, d)
            newEnv = extendEnv(n, v, env)
            return evalInEnv(newEnv, i)
        
        case Name(n):
            v = lookupEnv(n, env)
            if v is None:
                raise EvalError(f"unbound name {n}")
            
            return v
        
        # Boolean Evals
        # ______________________________________________
        case If(c, t, e):
            match evalInEnv(env, c):
                case bool(cond_val):
                    if cond_val:
                        return evalInEnv(env, t)
                    else:
                        return evalInEnv(env, e)
                case _:
                    raise EvalError("condition in if expression must be a boolean")

        case Or(l, r):
            match evalInEnv(env, l):
                case bool(True):
                    return True
                case bool(False):
                    match evalInEnv(env, r):
                        case bool(rv):
                            return rv
                        case _:
                            raise EvalError("or requires boolean operands")
                case _:
                    raise EvalError("or requires boolean operands")

        case And(l, r):
            match evalInEnv(env, l):
                case bool(False):
                    return False
                case bool(True):
                    match evalInEnv(env, r):
                        case bool(rv):
                            return rv
                        case _:
                            raise EvalError("and requires boolean operands")
                case _:
                    raise EvalError("and requires boolean operands")
        case Not(s):
            match evalInEnv(env, s):
                case bool(v):
                    return not v
                case _:
                    raise EvalError("not requires a boolean operand")

        case Eq(l, r):
            match (evalInEnv(env, l), evalInEnv(env, r)):
                case (lv, rv) if (type(lv) == type(rv) or (isinstance(lv, int) and isinstance(rv, int))):
                    return lv == rv
                case _:
                    raise EvalError("== requires operands of the same type")

                
        # Function Evals
        # ______________________________________________         
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
        
        # Domain Evals
        # ______________________________________________

        case Melody(notes):
            evaluated_notes = []
            for note in notes:
                pitch, duration = note
                evaluated_duration = evalInEnv(env, duration)
                evaluated_notes.append((pitch, evaluated_duration))
            return Melody(tuple(evaluated_notes))
        
        case Append(l, r):
            match (evalInEnv(env, l), evalInEnv(env, r)):
                case (Melody(lm), Melody(rm)):
                    return Melody(lm + rm)
                case _:
                    raise EvalError("append operation requires two melodies")

        case Repeat(count, melody):
            count_val = evalInEnv(env, count)

            if not isinstance(count_val, int):
                raise EvalError(f"Repeat count should be an integer, got {type(count_val)}")

            melody_val = evalInEnv(env, melody)
            match (count_val, melody_val):
                case (int(i), Melody(mel)):
                    if i < 0:
                        raise EvalError("repeat count cannot be negative")
                    return Melody(mel * i)
                case _:
                    raise EvalError("repeat operation requires an integer count and a melody")


def note_name_to_midi(note: str) -> int:
    note_to_midi = {
        "C": 60, "C#": 61, "D": 62, "D#": 63, "E": 64, "F": 65, "F#": 66,
        "G": 67, "G#": 68, "A": 69, "A#": 70, "B": 71
    }
    if note in note_to_midi:
        return note_to_midi[note]
    else:
        raise ValueError(f"Invalid note name: {note}")        


def run(e: Expr) -> None:
    print(f"running: {e}")
    try:
        env = emptyEnv

        # Create a MIDI file and set up the track
        midi = MIDIFile(1)  # One track
        track = 0
        midi.addTempo(track, 0, 120)  # Set the tempo, 120 BPM
        match evalInEnv(env, e):

            case Melody(notes):
                print(f"Generated melody: {notes}")

                midi_file = "output.mid"
                time = 0  # Track time in beats

                for pitch, duration in notes:
                    if pitch == 'R':  # Rest: Advance time without adding a note
                        time += duration
                    else:
                        midi_note = note_name_to_midi(pitch)
                        midi.addNote(track=0, channel=0, pitch=midi_note, time=time, duration=duration, volume=100)
                        time += duration

                with open(midi_file, "wb") as f:
                    midi.writeFile(f)

                # Please note that this just opens the default media
                # player on whatever machine you are running the interpretter on.
                # This default player MAY NOT SUPPORT midi files natively. 
                # I am using the legacy windows media player to listen to the
                # generated melodies.
                os.startfile(midi_file)

            case int(i):
                print(f"result: {i}")
            
            case bool(b):
                print(f"result: {b}")

            case float(f):
                print(f"result: {f}")
        
    except EvalError as err:
        print(f"Evaluation error: {err}")