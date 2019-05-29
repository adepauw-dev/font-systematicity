from itertools import combinations
from distance import EuclideanDistance, EditDistance

""" Sonorant, Consonantal, Voice, Nasal, Degree, Labial, Palatal, Pharyngeal, Round, Tongue, Radical, """
phonemes = {
    'a': [1, -1, 1, 0, -1, -1, 0, 1, -1, -1, 1],
    'b': [-1, 1, 0, -1, 1, 1, 0, -1, 1, 0, 0],
    'c': [-1, 1, -1, -1, 1, -1, -1, -1, -1, -1, 0],
    'd': [-1, 1, 0, -1, 1, -1, 1, -1, -1, 1, 0],
    'e': [1, -1, 1, 0, -1, -1, 0, -1, -1, -1, -1],
    'f': [-0.5, 1, -1, -1, 0, -1, 1, -1, 1, 0, 0],
    'g': [-1, 1, 0, -1, 1, -1, -1, -1, -1, -1, 0],
    'h': [-0.5, 1, 0, -1, 0, -1, -1, 1, -1, -1, -1],
    'i': [1, -1, 1, 0, 0, -1, 0, -1, -1, 0, -1],
    'j': [-0.8, 1, 0, -1, 1, -1, 0, -1, -1, 0, 0],
    'k': [-1, 1, -1, -1, 1, -1, -1, -1, -1, -1, 0],
    'l': [0.5, 0, 1, 0, -1, -1, 1, -1, -1, 1, 0],
    'm': [0, 0, 1, 1, 1, 1, 0, -1, 1, 0, 0],
    'n': [0, 0, 1, 1, 1, -1, 1, -1, -1, 1, 0],
    'o': [1, -1, 1, 0, -1, -1, -1, 1, -1, -1, -1],
    'p': [-1, 1, -1, -1, 1, 1, 0, -1, 1, 0, 0],    
    'r': [0.5, 0, 1, 0, -1, -1, -1, 1, 1, -1, -1],
    's': [-0.5, 1, -1, -1, 0, -1, 1, -1, -1, 1, 0],
    't': [-1, 1, -1, -1, 1, -1, 1, -1, -1, 1, 0],
    'u': [1, -1, 1, 0, -1, -1, -1, -1, -1, -1, -1],
    'v': [-0.5, 1, 0, -1, 0, -1, 1, -1, 1, 0, 0],
    'w': [0.8, 0, 1, 0, 0, 1, -1, -1, 1, -1, 0],
    'y': [0.8, 0, 1, 0, 0, -1, 0, -1, -1, 0, 1],
    'z': [-0.5, 1, 0, -1, 0, -1, 1, -1, -1, 1, 0],
}

def get_phonetic_distances():
    pairs = combinations(phonemes.keys(), 2)
    distances = {}
    for pair in pairs:
        char1 = pair[0]
        char2 = pair[1]
        phoneme1 = phonemes[char1]
        phoneme2 = phonemes[char2]

        edit_distance = EditDistance.get_distance(phoneme1, phoneme2)
        euclidean_distance = EuclideanDistance.get_distance(phoneme1, phoneme2)
        distances[(char1, char2)] = (edit_distance, euclidean_distance)

    return distances