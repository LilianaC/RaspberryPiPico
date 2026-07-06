#Instala la librería de pretty_midi
#Referencia https://crimier.github.io/posts/miditofreqs/
#pip install pretty_midi

import math
import pretty_midi
midi_data = pretty_midi.PrettyMIDI('/content/1940.mid')

freqs = []

prev_end = 0
for note in midi_data.instruments[0].notes:
    delay = note.start - prev_end
    if delay != 0:
        #print(delay)
        freqs.append((0, float(round(delay, 2))),)
    #print(note, pretty_midi.note_number_to_hz(note.pitch))
    freq = pretty_midi.note_number_to_hz(note.pitch)
    duration = note.end-note.start
    freqs.append((round(freq, 2), float(round(duration, 2))),)
    prev_end = note.end

print(freqs) # this is our list of freq/duration
