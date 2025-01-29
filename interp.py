'''
Tunes This DSL is for composing simple major mode melodies algorithmically.
Values: Tunes, which are sequences of (pitch,duration) pairs. Pitches correspond to keys on the piano;
durations are in seconds.
Literals: Tunes represented as an explicit sequence of (pitch name,duration) pairs, where pitch names
C,D,E,F,G,A,B represent the keys of the major scale starting at middle C and durations are integers. The
pseudo-pitch R can be used to represent a rest of the specified duration.
Operators: (i) concatenate two tunes so they are heard one after the other; (ii) transpose a tune up or down
by a specified number of half-steps.
Implementation: Use the Python midiutil package. See https://midiutil.readthedocs.io/
en/1.2.1/ to get started.
Result of evaluation: Output the tune as a one-track midi file called answer.midi; if possible automati-
cally open an app (such as GarageBand on MacOS or Windows Media Player) to play it.
Possible additions: accidentals, multiple simultaneous tunes (counterpoint!), chords(harmony!), dynamics,
etc., etc.
'''

from midiutil import MIDIFile
from dataclasses import dataclass
from typing import Any
import subprocess

NOTE_MAP = {
    "C": 60, "D": 62, "E": 64, "F": 65, "G": 67, "A": 69, "B": 71, "R": -1
}

type Literal = int | bool

type Expr = Add | Sub | Mul | Div | Neg | Lit | Let | Name | Or | And | Not | Eq | Lt | Play

#____________________________________________________________________________________________________________________________
#
# Types & Definitions
#____________________________________________________________________________________________________________________________

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
    
@dataclass
class If():
    pass

    b: bool
    t: Any
    e: Any

    def __str__(self) -> str:
        if self.b == True:
            return self.t
        return self.e

        
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
class Eq():
    left: Any
    right: Any

    def __str__(self) -> str:
        if self.left == self.right:
            return "True"
        return "False"

@dataclass
class Lt():
    left: int
    right: int

    def __str__(self) -> str:
        if self.left < self.right:
            return "True"
        return "False"

@dataclass
class Melody:
    notes: tuple[tuple[str, int], ...]  # Tuple of (pitch, duration) pairs

@dataclass
class Append:
    left: Melody
    right: Melody

@dataclass
class Repeat:
    count: int
    melody: Melody

@dataclass
class Play():
    pitch: str
    duration: int

    def __str__(self) -> str:
        return f"play({self.pitch}, {self.duration})"

    def to_midi(self, track: int, time: float, midi: MIDIFile) -> float:
        """Adds this note to a MIDI file."""
        midi_pitch = NOTE_MAP.get(self.pitch)
        if midi_pitch > 0: # If the value passed is not a rest
            midi.addNote(track, channel=0, pitch = midi_pitch, time = time, duration = self.duration, volume=100)

        return time + self.duration  # Advance time by note duration



#____________________________________________________________________________________________________________________________
#
# Environment & Compiler
#____________________________________________________________________________________________________________________________

class CompilerError(Exception):
    pass

class EvalError(Exception):
    pass

type Value = bool | int | float | Melody
type Binding[V] = tuple[str, V]  # A pair of name and value
type Env[V] = tuple[Binding[V], ...]  # An environment is a tuple of bindings

emptyEnv: Env[Any] = ()  # The empty environment has no bindings

def extendEnv[V](name: str, value: V, env: Env[V]) -> Env[V]:
    """Extend environment with a new variable."""
    return ((name, value),) + env

def lookupEnv[V](name: str, env: Env[V]) -> V | None:
    """Look up a variable in the environment."""
    for n, v in env:
        if n == name:
            return v
    return None

def evalInEnv(env: Env[Value], e: Expr, midi: MIDIFile, track: int, time: float) -> Value:
    match e:

        # Integer Evals
        # ______________________________________________
        case Add(l, r):
            match (evalInEnv(env, l, midi, track, time), evalInEnv(env, r, midi, track, time)):
                case (int(lv), int(rv)):
                    return lv + rv
                case _:
                    raise EvalError("addition of non-integers")
        
        case Sub(l, r):
            match (evalInEnv(env, l, midi, track, time), evalInEnv(env, r, midi, track, time)):
                case (int(lv), int(rv)):
                    return lv - rv
                case _:
                    raise EvalError("subtraction of non-integers")

        case Mul(l, r):
            match (evalInEnv(env, l, midi, track, time), evalInEnv(env, r, midi, track, time)):
                case (int(lv), int(rv)):
                    return lv * rv
                case _:
                    raise EvalError("multiplication of non-integers")
                
        case Div(l, r):
            match (evalInEnv(env, l, midi, track, time), evalInEnv(env, r, midi, track, time)):
                case (int(lv), int(rv)):
                    if rv == 0:
                        raise EvalError("division by zero")
                    return lv // rv
                case _:
                    raise EvalError("division of non-integers") 
                               
        case Neg(s):
            match evalInEnv(env, s, midi, track, time):
                case int(i):
                    return -i
                case _:
                    raise EvalError("negation of non-integer")

        # Variable Evals
        # ______________________________________________
        case Lit(lit):
            if isinstance(lit, (int, bool)):  # Only allow integers and booleans
                return lit
            else:
                raise EvalError(f"unexpected literal type: {type(lit)}")

        case Name(n):
            v = lookupEnv(n, env)
            if v is None:
                raise EvalError(f"unbound name {n}")
            return v

        case Let(n, d, b):
            v = evalInEnv(env, d, midi, track, time)  # Pass midi, track, time to inner evalInEnv
            newEnv = extendEnv(n, v, env)
            return evalInEnv(newEnv, b, midi, track, time)  # Pass midi, track, time to inner evalInEnv
        
        # Boolean Evals
        # ______________________________________________
        case And(l, r):
            left_val = evalInEnv(env, l, midi, track, time)
            if not isinstance(left_val, bool):  # Ensure it's a boolean
                raise EvalError(f"expected boolean type, got {type(left_val)} instead")
            if not left_val:
                return False  # Short-circuit, no need to evaluate right operand
            right_val = evalInEnv(env, r, midi, track, time)
            if not isinstance(right_val, bool):
                raise EvalError(f"expected boolean type, got {type(right_val)} instead")
            return right_val

        case Or(l, r):
            left_val = evalInEnv(env, l, midi, track, time)
            if not isinstance(left_val, bool):  # Ensure it's a boolean
                raise EvalError(f"expected boolean type, got {type(left_val)} instead")
            if left_val:
                return True  # Short-circuit, no need to evaluate right operand
            right_val = evalInEnv(env, r, midi, track, time)
            if not isinstance(right_val, bool):
                raise EvalError(f"expected boolean type, got {type(right_val)} instead")
            return right_val

        case Not(s):
            val = evalInEnv(env, s, midi, track, time)
            if not isinstance(val, bool):  # Ensure it's a boolean
                raise EvalError(f"expected boolean type, got {type(val)} instead")
            return not val
        
        case Eq(l, r):
            left_val = evalInEnv(env, l, midi, track, time)
            right_val = evalInEnv(env, r, midi, track, time)
            
            if type(left_val) != type(right_val):
                return False  # If types are different, they are not equal
            
            if isinstance(left_val, Melody) and isinstance(right_val, Melody):
                return left_val.notes == right_val.notes

            else:
                return left_val == right_val
        
        case Lt(l, r):
            left_val = evalInEnv(env, l, midi, track, time)
            right_val = evalInEnv(env, r, midi, track, time)

            if not isinstance(left_val, int) or not isinstance(right_val, int):
                raise EvalError(f"expected two integers for comparison")
            
            return left_val < right_val
        
        case If(b, t, e):
            cond_val = evalInEnv(env, b, midi, track, time)

            if not isinstance(cond_val, bool):
                raise EvalError(f"expected boolean type, got {type(cond_val)}")

            # Short-circuit --  evaluate 't' or 'e' based on the condition 'b'
            if cond_val:
                return evalInEnv(env, t, midi, track, time)  # Returns then branch
            else:
                return evalInEnv(env, e, midi, track, time)  # Returns else branch


        # Domain Evals
        # ______________________________________________
        case Append(left, right):
            match (evalInEnv(env, left, midi, track, time), evalInEnv(env, right, midi, track, time)):
                case (Melody(lm), Melody(rm)):  # Ensure both sides are melodies
                    return Melody(lm.notes + rm.notes)  # Concatenating the notes
                case _:
                    raise EvalError("append operation requires two melodies")

        case Repeat(count, melody):
            match (evalInEnv(env, count, midi, track, time), evalInEnv(env, melody, midi, track, time)):
                case (int(i), Melody(mel)):
                    repeated_notes = mel.notes * i  # Repeat the notes, not the whole Melody object
                    return Melody(repeated_notes)  # Create a new Melody with repeated notes
                case _:
                    raise EvalError("repeat operation requires an integer count and a melody")

        case Play(pitch, duration):
            # Here you evaluate the Play expression and add it to the MIDI file
            midi_pitch = NOTE_MAP.get(pitch)
            if midi_pitch > 0:
                midi.addNote(track, channel=0, pitch=midi_pitch, time=time, duration=duration, volume=100)

            return time + duration

        case _:
            raise EvalError(f"Unsupported expression type: {e}")
        

#____________________________________________________________________________________________________________________________
#
# Program execution & test cases
#____________________________________________________________________________________________________________________________


def run(e: Expr) -> None:
    print(f"Running expression: {e}")
    
    try:
        env = emptyEnv

        # Create a MIDI file and set up the track
        midi = MIDIFile(1)  # One track
        track = 0
        midi.addTempo(track, 0, 120)  # Set the tempo, 120 BPM
        match evalInEnv(env, e, midi=midi, track=track, time=0.0):
            case Melody(m):
                print(f"Generated melody: {m.notes}")
            
                # Save the MIDI file
                midi_file = "output.mid"
                with open(midi_file, "wb") as f:
                    midi.writeFile(f)

                # Play the MIDI file using VLC
                subprocess.run(["vlc", midi_file])

            case int(i):
                print(f"result: {i}")
            
            case bool(b):
                print(f"result: {b}")

            case float(f):
                print(f"result: {f}")
        
    except EvalError as err:
        print(f"Evaluation error: {err}")



a : Expr = Let('x', Add(Lit(1), Lit(2)), 
                    Sub(Name('x'), Lit(3)))

b : Expr = Let('x', Lit(1), 
                    Let('x', Lit(2), 
                             Mul(Name('x'), Lit(3))))


c : Expr = Append(
        Play(pitch='C', duration=1),
        Play(pitch='G', duration=2)
    )

d: Expr = Let(
    'melody', 
    Append(
        Play(pitch='C', duration=1),
        Play(pitch='G', duration=1),
    ),
    Append(
        Name('melody'),  # Append the second melody to the first one
        Play(pitch='C', duration=1),
    )
)

run(a)
run(b)
run(c)


'''
For my domain specific extension I chose the music domain. My language SHOULD be able to accept notes and durations, and be able to 
concatanate and repeat melodies. I was not able to get it to a working state in time for the milestone, however all of the pieces should be present
as I tested each induvidually while devleoping this document. All of the arithmitic should be up and running, however due to the structure of my 
evalInEnv() function I have more arguments than the test driver causing it to fail many tests. 
'''