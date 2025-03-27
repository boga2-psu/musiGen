from dataclasses import dataclass
from typing import Any
import numpy as np
import sounddevice as sd

type Expr = Add | Sub | Mul | Div | Neg | Lit | Let | Name | If | Or | And | Not | Eq | Lt | Assign | Read | Seq | Letfun | App | Show | Melody | Play | Append | Repeat | Chorus
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
class Assign:
    expr1: Expr
    expr2: Expr

    def __str__(self) -> str:
        return f"({self.expr1} := {self.expr2})"

@dataclass
class Read:
    def __str__(self) -> str:
        return "read"

@dataclass
class Seq():
    expr1: Expr
    expr2: Expr
    def __str__(self) -> str:
        return f"({self.expr1} ; {self.expr2})"
    
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
class Show:
    expr: Expr

    def __str__(self) -> str:
        return f"(show {self.expr})"
    
@dataclass
class Melody:
    notes: tuple[tuple[str, int], ...]  # Tuple of (pitch, duration) pairs

    def __str__(self) -> str:
        note_strs = [f"{pitch}{duration}" for pitch, duration in self.notes]
        return "[" + " ".join(note_strs) + "]"
    
    def __iter__(self):
        return iter(self.notes)
    
@dataclass
class Play:
    melody: Expr

    def __str__(self) -> str:
        return f"(playing {self.melody})"

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

@dataclass
class Chorus:
    melody: Expr

    def __str__(self) -> str:
        return f"(chorus effect {self.melody})"

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

# models memory locations as (mutable) singleton lists
type Loc[V] = list[V] # always a singleton list
def newLoc[V](value: V) -> Loc[V]:
    return [value]
def getLoc[V](loc: Loc[V]) -> V:
    return loc[0]
def setLoc[V](loc: Loc[V], value: V) -> None:
    loc[0] = value

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
        case Lit(i):
                return i
        
        case Let(n,d,i):  
            v = evalInEnv(env, d)
            loc = newLoc(v)
            newEnv = extendEnv(n, loc, env)
            return evalInEnv(newEnv, i)
        
        case Name(n):
            v = lookupEnv(n, env)
            if v is None:
                raise EvalError(f"unbound name {n}")
            
            return getLoc(v)
        
        case Assign(x,e):
            loc_x = lookupEnv(x, env)
            if loc_x is None:
                raise EvalError(f"Cannot assign to unbound name {n}")
            
            if isinstance(getLoc(l), Closure):  # Prevents modifying function bindings
                raise EvalError(f"Cannot assign to function name {n}")
            
            expr = evalInEnv(env, e)
            setLoc(loc_x, expr)

            return expr
        
        case Read():
            try:
                user_input = input("Enter an integer: ")
                return int(user_input)
            except ValueError:
                raise EvalError("read operation failed: input is not a valid integer")

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
            loc = newLoc(c)
            newEnv = extendEnv(n,loc,env)
            c.env = newEnv        
            return evalInEnv(newEnv,i)
        
        case App(f,a):
            fun = evalInEnv(env,f)
            arg = evalInEnv(env,a)
            match fun:
                case Closure(p,b,cenv):
                    loc = newLoc(arg)
                    newEnv = extendEnv(p,loc,cenv) 
                    return evalInEnv(newEnv,b)
                case _:
                    raise EvalError("application of non-function")
                
        case Seq(e1, e2):
            evalInEnv(env, e1)
            return evalInEnv(env,e2)
        
        case Show(expr):
            v = evalInEnv(env, expr)
            
            print(f"showing {v}")
            if isinstance(v, Melody) or (isinstance(v, list) and all(isinstance(mel, Melody) for mel in v)):
                play_melody(v)

            return v
        
        # Domain Evals
        # ______________________________________________
        case Melody(notes):
            evaluated_notes = []
            for note in notes:
                pitch, duration = note
                if isinstance(duration, Lit):
                    duration_value = duration.value  # Extract value from Lit
                else:
                    duration_value = evalInEnv(env, duration)  # Evaluate if it's not a Lit
                evaluated_notes.append((pitch, duration_value))
            print(f"Evaluated melody: {evaluated_notes}")
            return Melody(tuple(evaluated_notes))

        case Play(m):
            melody = evalInEnv(env, m)
            
            if isinstance(melody, Melody) or (isinstance(melody, list) and all(isinstance(mel, Melody) for mel in melody)):
                return Play(melody)
            else:
                raise EvalError(f"Play operation requires a Melody, got {type(melody)}")

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
            if not isinstance(melody_val, Melody):
                raise EvalError("Repeat operation requires a melody, got {type(melody_val)}")
                
            if count_val < 0:
                raise EvalError("Repeat count cannot be negative")
            
            return Melody(melody_val.notes * count_val)
        
        case Chorus(melody):
            melody_val = evalInEnv(env, melody)

            if not isinstance(melody_val, Melody):
                raise EvalError(f"Chorus requires a Melody, got {type(melody_val)}")

            original = melody_val.notes
            lower = [(f"{pitch}-1", duration) for pitch, duration in original]
            higher = [(f"{pitch}+1", duration) for pitch, duration in original]

            chorus_effect = [Melody(original), Melody(lower), Melody(higher)]

            return chorus_effect


def note_to_freq(note: str) -> float:
    # We will define our base frequency as A4
    base_freq = 440.0  
    # Whole step frequency ratio (12th root of 2)
    ratio = 2 ** (1/12) 

    notes = ["A", "B", "C", "D", "E", "F", "G"]
    
    if note == "R":
        return None
    
    # Check for an octave shift
    if note[-2:] in ["+1", "-1"]:
        pitch = note[:-2]
        octave_shift = int(note[-2:])
    else:
        pitch = note
        octave_shift = 0
    
    if pitch not in notes:
        raise ValueError(f"Invalid note name: {pitch}")
    
    note_index = notes.index(pitch)

    # Calculates the note's frequency based on the given Concert A (440hz) with any pitch shifting in mind
    freq = base_freq * (ratio ** note_index) * (4 ** octave_shift)
    return freq


def generate_sin_wave(freq: float, duration: float, sample_rate: int = 44100) -> np.ndarray:
    if freq is None:
        return np.zeros(int(sample_rate * duration)) 

    # Creates a numpy array to store the waveforms in
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    # Generates the sin wave based on the frequency provided
    sin_wave = np.sin(2 * np.pi * freq * t)
    # Creates an evelope around the wave to eliminate popping
    envelope = adsr_envelope(duration, sample_rate)

    return sin_wave * envelope


# Creates an Attack, Decay, Sustain Release envelope for a given wave
def adsr_envelope(duration, sample_rate, attack=0.1, decay=0.1, sustain=0.6, release=0.1):
    
    total_samples = int(duration * sample_rate)  # Convert duration to samples

    attack_samples = int(sample_rate * attack)
    decay_samples = int(sample_rate * decay)
    release_samples = int(sample_rate * release)
    
    # Ensure sustain lasts for the remaining time
    sustain_samples = max(0, total_samples - (attack_samples + decay_samples + release_samples))

    # Create an envelope of the correct size
    envelope = np.zeros(total_samples)

    # Define ADSR segments
    envelope[:attack_samples] = np.linspace(0, 1, attack_samples, endpoint=False)
    envelope[attack_samples:attack_samples + decay_samples] = np.linspace(1, sustain, decay_samples, endpoint=False)
    envelope[attack_samples + decay_samples:attack_samples + decay_samples + sustain_samples] = sustain
    envelope[attack_samples + decay_samples + sustain_samples:] = np.linspace(sustain, 0, release_samples)

    return envelope


def play_melody(melody, sample_rate: int = 44100, bpm: int = 120):
    
    # Checks and plays a single melody object 
    if isinstance(melody, Melody):  
        audio = np.array([])
        for pitch, duration in melody.notes:
            freq = note_to_freq(pitch)
            #duration *= (60 / (bpm * 2)) # adjusting the duration to eighth notes instead of seconds
            
            if freq is None:
                wave = np.zeros(int(sample_rate * duration))
            else:
                wave = generate_sin_wave(freq, duration, sample_rate)
            
            audio = np.append(audio, wave)

        final_audio = audio  

    # Checks and plays a list of melodies (from Chorus)
    elif isinstance(melody, list) and all(isinstance(m, Melody) for m in melody):  
        audio_layers = []

        for m in melody:
            audio = np.array([])  
            for pitch, duration in m.notes:
                freq = note_to_freq(pitch)
                #duration *= (60 / (bpm * 2)) # adjusting the duration to eighth notes instead of seconds

                if freq is None:
                    wave = np.zeros(int(sample_rate * duration))
                else:
                    wave = generate_sin_wave(freq, duration, sample_rate)
                
                audio = np.append(audio, wave)
            
            audio_layers.append(audio)

        # Sums layers and normalizes volume to avoid waves clipping!
        final_audio = sum(audio_layers) / len(audio_layers)

    else:
        raise ValueError(f"Invalid input to play_melody: {type(melody)}")

    # Play the resulting audio
    sd.play(final_audio, sample_rate)
    sd.wait()

def run(e: Expr) -> None:
    print(f"running: {e}")
    try:
        env = emptyEnv
        match evalInEnv(env, e):

            case Play(m):
                if isinstance(m, Melody):
                    print(f"Playing melody {m}")

                elif isinstance(m, list) and all(isinstance(mel, Melody) for mel in m):
                    print("Layering these melodies:")
                    for melody in m:
                        print(f"Playing melody {melody}")

                try:
                    play_melody(m)
                    print("Melody played successfully.")
                except ValueError as e:
                    # Handle errors (e.g., invalid note names in the melody)
                    print(f"Error playing melody: {e}")
                except Exception as e:
                    # Catch any other exceptions that might occur during playback
                    print(f"Unexpected error: {e}")

            case Melody(notes):
                print(f"Computed melody: {notes}")

            case int(i):
                print(f"result: {i}")
            
            case bool(b):
                print(f"result: {b}")

            case float(f):
                print(f"result: {f}")
        
    except EvalError as err:
        print(f"Evaluation error: {err}")