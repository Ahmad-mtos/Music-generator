from functools import partial
import math
from mido import MidiFile, MidiTrack, Message
from random import choice, choices, randint, randrange, random
from typing import List, Optional, Callable, Tuple
import music21
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame

# Typings and lists and dicunaries that help throghout the code
Genome = List[tuple]
Population = List[Genome]
PopulateFunc = Callable[[], Population]
FitnessFunc = Callable[[Genome], int]
notes = {'C':48, 'C#':49, 'D':50, 'E':52, 'F':53, 'G':55, 'A':57, 'B':59}
major_offset = [2, 2, 1, 2, 2, 2]
minor_offset = [2, 1, 2, 2, 1, 2]
key = []

# Figures out the key of the melody
def figure_key (root: int, type: str):
    ret = [root]
    if type=='minor':
        for offset in major_offset:
            root+= offset
            ret.append(root)
    elif type=='major':
        for offset in minor_offset:
            root+= offset
            ret.append(root)
    return ret

# Generates a major chord and its first and second inversion
def generate_major(first: int) ->tuple:
    first = key[first]
    first-=12
    probability = randint(0,9)
    if probability >6:
        major = (first+12, first+16, first+7)
    elif probability >3:
        major = (first+12, first+4, first+7)
    else:
        major = (first, first+4, first+7)
    return major

# Generates a minor chord and its first and second inversion
def generate_minor(first: int) -> tuple:
    first = key[first]
    first-=12
    probability = randint(0,9)
    if probability >6:
        minor = (first+12, first+15, first+7)
    elif probability >3:
        minor = (first+12, first+3, first+7)
    else:
        minor = (first, first+3, first+7)
    return minor

# Generates a diminished chord
def generate_diminished(first: int) -> tuple:
    first = key[first]
    first-=12
    diminished = (first, first+3, first+6)
    return diminished

# Generates a sus2 chord
def generate_sus2(first: int) -> tuple:
    first = key[first]
    first-=12
    probability = randint(0,9)
    if probability >6:
        sus2 = (first+12, first+14, first+7)
    elif probability >3:
        sus2 = (first+12, first+2, first+7)
    else:
        sus2 = (first, first+2, first+7)
    return sus2

# Generates a sus4 chord
def generate_sus4(first: int) -> tuple:
    first = key[first]
    first-=12
    probability = randint(0,9)
    if probability >6:
        sus4 = (first+12, first+17, first+7)
    elif probability >3:
        sus4 = (first+12, first+5, first+7)
    else:
        sus4 = (first, first+5, first+7)
    return sus4

# Generates a chord with the help of the previous functions
def generate_chord(key_type: str) -> tuple:
    choice = randint(0,3)
    first = randint(0,6)
    if (key_type== "minor" and first == 1) or (key_type== "major" and first == 6):
        return generate_diminished(first)
    if choice==0:
        return (generate_major(first))
    elif choice==1:
        return (generate_minor(first))
    elif choice==2:
        return generate_sus2(first)
    elif choice==3:
        return generate_sus4(first)

# Generates a genome of chords created using the latter function
def generate_genome(length: int, key_type: str) -> Genome:
    genome= []
    for i in range(length):
        genome.append(generate_chord(key_type))
    return genome

# Generates a population of genomes using the latter function
def generate_population(size: int, genome_length: int, key_type: str) -> Population:
    return [generate_genome(genome_length, key_type) for _ in range(size)]

# A function that checks if two notes are the same (even from different octaves), returns true if so, false otherwise
def same_note (a:int, b:int) -> bool:
    if ((abs(a-b)%12)==0):
        return True
    return False

# A function that checks if a chord and a note create a dissonance, returns true if so, false otherwise
def dissonance (chord: tuple, note: int) -> bool:
    dissonant= [1, 2, 6, 10, 11]
    for i in range(3):
        if ((abs(chord[i]-note))%12) in dissonant:
            return True
    return False

# A fitness function, that rewards the genome for having similar notes, and penalize it for having dissonance. returns an integer representing the fitness value of the genome
def fitness(genome: Genome, delay: int, track: MidiTrack) -> int:
    value = 0
    j = 0
    melody_time =0 
    acc_time =0
    for chord in genome:
        acc_time+=delay
        while melody_time<acc_time:
            if j >= len(track):
                break
            melody_time+= track[j].time
            if (track[j].type == 'note_off'):
                if (dissonance(chord, track[j].note)):
                    value-=50
                note= track[j].note
                if (same_note(note,chord[0]) or same_note(note, chord[1]) or same_note(note, chord[2])):
                    value+=5
            j+=1
        
    return value


# The crossover function that swaps the genes of two genomes at a random point, returns a tuple of the new genomes
def single_point_crossover(a: Genome, b: Genome) -> Tuple[Genome, Genome]:
    length = len(a)
    if length < 2:
        return a, b

    p = randint(1, length - 1)
    return a[0:p] + b[p:], b[0:p] + a[p:]

# A mutation function that mutates a genome with a fixed probability. Returns the new genome
def mutation(genome: Genome, probability: float = 0.5) -> Genome:
    index = randrange(len(genome))
    genome[index] = genome[index] if random() > probability else generate_chord(key_type=zob.analyze('key').mode)
    return genome

# The selection function that selects two genomes out of the population and prefers the genomes with highest fitness scores
def selection_pair(population: Population, fitness_func: FitnessFunc) -> Population:
    return choices(
        population=population,
        weights=[fitness_func(gene) for gene in population],
        k=2
    )


# A function that sorts the population in accordance to their fitness score
def sort_population(population: Population, fitness_func: FitnessFunc) -> Population:
    return sorted(population, key=fitness_func, reverse=True)



# A function that runs the evolution for a given number of generations (200 if not declared). Returns the population of the last generation
def run_evolution(
        populate_func: PopulateFunc,
        fitness_func: FitnessFunc,
        generation_limit: int = 400
        ) \
        -> Population:
    population = populate_func()

    for i in range(generation_limit):
        population = sorted(population, key=lambda genome: fitness_func(genome), reverse=True)

        next_generation = population[0:2]

        for j in range(int(len(population) / 2) - 1):
            parents = selection_pair(population, fitness_func)
            offspring_a, offspring_b = single_point_crossover(parents[0], parents[1])
            offspring_a = mutation(offspring_a)
            offspring_b = mutation(offspring_b)
            next_generation += [offspring_a, offspring_b]

        population = next_generation

    population = sorted(population, key=lambda genome: fitness_func(genome), reverse=True)
    return population

# A funtion that takes a genome and converts it to a midi track, that will be later merged with the original track. Returns the converted miditrack
def convert_to_track (genome: Genome, delay: int) -> MidiTrack:
    track = MidiTrack()
    for chord in genome:
        track.append(Message('note_on', note= chord[0], velocity= 64, time= 0))
        track.append(Message('note_on', note= chord[1], velocity= 64, time= 0))
        track.append(Message('note_on', note= chord[2], velocity= 64, time= 0))
        track.append(Message('note_off', note= chord[0], velocity= 64, time= delay))
        track.append(Message('note_off', note= chord[1], velocity= 64, time= 0))
        track.append(Message('note_off', note= chord[2], velocity= 64, time= 0))
        
    return track

# A funtion to handle all the pre calculations necessary for the algorithm. Also calls run_evolution for the evolution to start
def preprocess(mid):
    cnt = 0
    boo = 2
    for msg in mid.tracks[1]:
        if msg.is_meta or msg.type == 'program_change':
            continue
        cnt = cnt + msg.time
    beats = math.ceil((cnt/mid.ticks_per_beat)/boo)
    print("Running the evolution (This might take some time):")
    population= run_evolution(
        populate_func= partial(generate_population, size= 60, genome_length = beats,key_type=zob.analyze('key').mode),
        fitness_func= partial(fitness, delay= 384*boo, track= mid.tracks[1])
    )
    mid.tracks.append(convert_to_track(population[0],384*boo))
    print("The output has been saved, the best fitness score found was:", fitness(population[0],384*boo, mid.tracks[1]))


def play_track (file_name):
    print (f"Playing track {file_name}:")
    try:
        init_pygame_music()
        pygame.mixer.music.load(file_name)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pass # check if playback has finished
        print ("Track finished playing.")
    except KeyboardInterrupt:
        print("Track interrupted...")
        pygame.mixer.music.stop()

def evolution (file_name):
    try:
        global key, zob
        mid = MidiFile(file_name, clip=True)
        zob = music21.converter.parse(file_name)
        key = figure_key(notes[zob.analyze('key').tonic.name], zob.analyze('key').mode)
        preprocess(mid)
        output = "out_" + file_name
        mid.save(output)
    except KeyboardInterrupt:
        print ("Evolution process interrupted...")

def init():
    try:
        print("Print a number corresponding to the option you want:")
        print("1) Do evolution magic!!")
        print("2) Play a track")
        print("3) Quit")
        option = int(input())
        if option == 1:
            print ("Choose the number of the track you want to add an accompaniment to:")
            temp = os.popen("ls | grep .mid").read()
            lst = temp.split('\n')[:-1]
            for i in range(len(lst)):
                print(f"{i}) {lst[i]}")
            track_num = int(input())
            evolution(lst[track_num])
        elif option == 2:
            print ("Choose the number of the track you want to play:")
            temp = os.popen("ls | grep .mid").read()
            lst = temp.split('\n')[:-1]
            for i in range(len(lst)):
                print(f"{i}) {lst[i]}")
            track_num = int(input())
            play_track(lst[track_num])
        elif option == 3:
            print("Bye bye!")
            exit(0)
        else:
            print("Invalid Option")
    except KeyboardInterrupt:
        print("Terminating the program...")
        exit(0)

def init_pygame_music ():
    freq = 44100
    bitsize = -16  
    channels = 1 
    buffer = 1024 
    pygame.init()
    pygame.mixer.init(freq, bitsize, channels, buffer)

while (True):
    init()