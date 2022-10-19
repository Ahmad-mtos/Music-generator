# Documentation

## Introduction
---
This program is designed to generate an accompinement to a music file that has only a melody.

### Input music file requirements

The file you should pass to the program should have the following:
- It should be a midi file (i.e. with .mid extention)
- It should only have a melody (the code might work with a file with an accompaniment, but the results are unreliable)
- The melody should be written in a non-changing tempo and time signature (4/4 aka C or common time).

### Run

To run the program, you just have to run the music_generator.py file. There are multiple example midi files you can test the code on.

## User Interface
---
After installing the necessary libraries (mentioned in the Manual section) to run the code, and running the program you will get 3 main options:

### Do evolution magic!!

This option will further ask you to choose a midi file (in the same directory) to run the evolutionary algorithm on. After the algorithm finishes its work, you will get a message informing you about the fitness score atained by the algorithm for this file (running the algorithm agian on the same file *might* give you a better result). The resulting file will be saved on the same directory under the name out_file_name.mid.

### Play a track

This option will further ask you to choose a midi file (in the same directory) to play. The chosen track will start playing until it's done, or you can force stop it (e.g. ctrl+c on terminal).

### Quit

This option will stop the program and exit.

## Evolutionary Algorithm
---
A genetic algorithm was used for the evolutionary algorithm

### Genome

The genome here is a list of tuples, each tuple repreasenting a chord: Major chord, Minor chord, sus2, sus4, or a diminished chore, with thier first and seoncd inversions.

### Population

A list of genomes

### Selection function

Two genomes of the population are picked at random, with weights giving the genomes with higher fitness value a favour.

### Crossover function

A single point crossover function was implemented. The two genomes, that were slected by the Selection function, are cut at a random point, and the genes are swapped after the cut between the two genomes.

### Mutation

With a probability of 50%, a genome may get mutated. The mutation process picks a random gene (chord) of the genome, and generates a new genome instead.

### Fitness function

The fitness function gives a reward if a note from the melody was the same in a chord that is playing simultaneously. It also gives a penalty if two notes were creating dissonance.

### Evolution details

The algorithm runs for 400 generation, with a population of 60 genomes. The fitness limit was uncapped since the optimal fitness value may vary from a track to another.


## Manual
---
Three external libraries are essensial for running the code.

### music21

Helps detect the key of the melody.
>pip3 install --upgrade music21

### mido
Helps deal with midi files, adding tracks and configuring notes.
>pip install mido

### pygame
Used to play tracks inside the code
>pip install pygame
## Citations
---
The EA code was adopted from the code provided in the following github ripo
>https://github.com/kiecodes/genetic-algorithms

The project in the repo was aimed to solve Knapsack with the help of EA. 