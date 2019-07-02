from itertools import combinations
from distance import EuclideanDistance, EditDistance
import data
from data import SoundDistance

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

        hamming_distance = EditDistance.get_distance(phoneme1, phoneme2)

        euclidean_distance = EuclideanDistance.get_distance(phoneme1, phoneme2)

        edit_distance = 0

        sum_distance = 0

        for i in range(len(phoneme1)):
            if (phoneme1[i] != phoneme2[i]):
                edit_distance += 1
            sum_distance += abs(phoneme1[i] - phoneme2[i])

        distances[(char1, char2)] = (hamming_distance, euclidean_distance, edit_distance, sum_distance)

    return distances

def calculate_sound_distances():
    sound_distances = get_phonetic_distances()
    distance_objects = []
    for key, item in sound_distances.items():
        sound_distance = SoundDistance(
            char1 = key[0],
            char2 = key[1],
            metric = "Hamming",
            distance = item[0]
        )
        distance_objects.append(sound_distance)
        
        sound_distance = SoundDistance(
            char1 = key[0],
            char2 = key[1],
            metric = "Euclidean",
            distance = item[1]
        )
        distance_objects.append(sound_distance)
        
        sound_distance = SoundDistance(
            char1 = key[0],
            char2 = key[1],
            metric = "Edit",
            distance = item[2]
        )
        distance_objects.append(sound_distance)
        
        sound_distance = SoundDistance(
            char1 = key[0],
            char2 = key[1],
            metric = "Edit_Sum",
            distance = item[3]
        )
        distance_objects.append(sound_distance)    

    with data.db.atomic():
        SoundDistance.bulk_create(distance_objects, batch_size=100)

if __name__ == "__main__":
    calculate_sound_distances()