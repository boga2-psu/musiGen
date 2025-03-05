# musiGen
A small language for performing arithmetic and writing to midi files


'''
Tunes: This DSL is for composing simple major mode melodies algorithmically.
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