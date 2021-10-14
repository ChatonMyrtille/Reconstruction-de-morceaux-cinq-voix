import numpy as np
import random as rnd
from mido import MidiFile
from mido import MidiTrack
from mido import Message

pitch = [
"A0", "A#0", "B0",
"C1", "C#1", "D1", "D#1", "E1", "F1", "F#1", "G1", "G#1", "A1", "A#1", "B1",
"C2", "C#2", "D2", "D#2", "E2", "F2", "F#2", "G2", "G#2", "A2", "A#2", "B2",
"C3", "C#3", "D3", "D#3", "E3", "F3", "F#3", "G3", "G#3", "A3", "A#3", "B3",
"C4", "C#4", "D4", "D#4", "E4", "F4", "F#4", "G4", "G#4", "A4", "A#4", "B4",
"C5", "C#5", "D5", "D#5", "E5", "F5", "F#5", "G5", "G#5", "A5", "A#5", "B5",
"C6", "C#6", "D6", "D#6", "E6", "F6", "F#6", "G6", "G#6", "A6", "A#6", "B6",
"C7", "C#7", "D7", "D#7", "E7", "F7", "F#7", "G7", "G#7", "A7", "A#7", "B7",
"C8"
]

duration = {
    0.5: "eighth\t\t",
    1.0: "quarter\t",
    1.5: "dotted quarter\t",
    2.0: "half\t\t",
    3.0: "dotted half\t",
    4.0: "whole\t\t",
    6.0: "dotted whole\t",
    8.0: "double whole\t",
    12.0: "dotted double whole"
}

durationIndex = ["eighth\t\t", "quarter\t", "dotted quarter\t", "half\t\t", "dotted half\t", "whole\t\t", "dotted whole\t", "double whole\t", "dotted double whole"]
durationBeats = [0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0, 8.0, 12.0]

class Note():
    
    def __init__(self, pitch, duration, position):
        self.pitch = pitch
        self.duration = duration
        self.position = position
        
    def __str__(self):
        return self.pitch + "\t " + self.duration + "\t" + str(self.position)

notes = []

midi = MidiFile("cmefta.mid")
for track in midi.tracks[:-1]:
    beats = 0
    for msg in track:
        if msg.type == "note_on":
            if msg.time != 0:
                beats += msg.time / (120*4)
        if msg.type == "note_off":
            print(beats/4)
            notes.append(Note(pitch[msg.note - 20 - 1], duration[msg.time / (120*4)], (int(beats//4) + 1, int(beats%4 + 1), int(((beats%4 + 1) % 1) * 4 + 1))))
            beats += msg.time / (120*4)

A = np.zeros(shape=(88,88))
for note in notes:
    for otherNote in notes:
        if otherNote.position == note.position:
            A[pitch.index(note.pitch)][pitch.index(otherNote.pitch)] += 1
            
B = np.zeros(shape=(9,9))
for i in range(len(notes)-1):
    B[durationIndex.index(notes[i].duration)][durationIndex.index(notes[i+1].duration)] += 1
    
C = np.zeros(shape=(9,2))
for i in range(len(notes)-1):
    position1 = (notes[i].position[0] - 1) * 4 + (notes[i].position[1] - 1) + (notes[i].position[2] - 1) * 0.25
    position2 = (notes[i+1].position[0] - 1) * 4 + (notes[i+1].position[1] - 1) + (notes[i+1].position[2] - 1) * 0.25
    if position1 + durationBeats[durationIndex.index(notes[i].duration)] < position2:
        C[durationIndex.index(notes[i].duration)][0] += 1
    else:
        C[durationIndex.index(notes[i].duration)][1] += 1
    
D = np.zeros(shape=(9,9))
for i in range(len(notes)-1):
    position1 = (notes[i].position[0] - 1) * 4 + (notes[i].position[1] - 1) + (notes[i].position[2] - 1) * 0.25
    position2 = (notes[i+1].position[0] - 1) * 4 + (notes[i+1].position[1] - 1) + (notes[i+1].position[2] - 1) * 0.25
    if position1 + durationBeats[durationIndex.index(notes[i].duration)] < position2:
        length = position2 - (position1 + durationBeats[durationIndex.index(notes[i].duration)])
        if length in duration:
            D[durationIndex.index(notes[i].duration)][durationBeats.index(length)] += 1

voice = MidiFile()
track = MidiTrack()
voice.tracks.append(track)

beats = 0
rest = 0
length = 4.0
while True:
    position = (int(beats//4) + 1, int(beats%4 + 1), int(((beats%4 + 1) % 1) * 4 + 1))
    if position[0] > 500:
        break
    
    proba = C[durationIndex.index(duration[length])]
    proba = proba / sum(proba)
    proba = proba.cumsum()
    p = rnd.random()
    silence = np.where(p < proba)[0][0]
    
    if silence == 0:
        proba = D[durationIndex.index(duration[length])]
        proba = proba / sum(proba)
        proba = proba.cumsum()
        p = rnd.random()
        silenceLength = durationBeats[np.where(p < proba)[0][0]]
        
        print(str(position) + " -> " + "rest" + " | " + duration[silenceLength])
        beats += silenceLength
        rest += silenceLength
    else:
        proba = np.zeros(shape=(88))
        for note in notes:
            if note.position == position:
                proba += A[pitch.index(note.pitch)]

        if sum(proba) != 0:
            proba = proba / sum(proba)
            proba = proba.cumsum()
            p = rnd.random()
            note = np.where(p < proba)[0][0]
                    
            proba = B[durationIndex.index(duration[length])]
            proba = proba / sum(proba)
            proba = proba.cumsum()
            p = rnd.random()
            length = durationBeats[np.where(p < proba)[0][0]]

            track.append(Message('note_on', note = note + 21, velocity = 80, time = int(rest * (120*4))))
            track.append(Message('note_off', note = note + 21, velocity = 64, time = int(length * (120*4))))
            print(str(position) + " -> " + pitch[note] + " | " + duration[length])
            rest = 0
            beats += length
        else:
            print(str(position) + " -> " + "rest" + " | " + "eighth")
            beats += 0.25
            rest += 0.25
                
voice.save("voice.mid")
