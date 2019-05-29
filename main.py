import os
from itertools import combinations

import numpy as np
from scipy.stats.stats import pearsonr

import morphemes
import phonemes
import visualization

def save_distance_images(haus, chars, bitmaps, i, j, path=".\\img\\pairs", save=True, show=False):
    # Generate visualizations of hausdorff distances
    contrib_points1 = [haus[0][1], haus[1][2]]
    contrib_points2 = [haus[0][2], haus[1][1]]
    bitmap = visualization.render_image_pair(chars[i], chars[j], bitmaps[i], bitmaps[j], contrib_points1, contrib_points2, haus[0][0], haus[1][0])
    if (save):
        visualization.save_image(bitmap, "{0}{1}".format(chars[i], chars[j]), path=path)
    if (show):
        visualization.show_image(bitmap)

if __name__ == "__main__":
    g = morphemes.GlyphRenderer("C:\\times.ttf")

    coords = None
    chars = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u", "v", "w", "y", "z"]
    
    bitmaps = g.bitmaps(chars, 192, coords)

    visual_distances = {}

    # Generate all pairs of chars and calculate distance
    pairs = list(combinations(range(len(chars)),2))
    for pair in pairs:
        i = pair[0]
        j = pair[1]
        haus = morphemes.hausdorff_distance(bitmaps[i], bitmaps[j])

        visual_distances[(chars[i], chars[j])] = max(haus[0][0], haus[1][0])
        #save_distance_images(haus, chars, bitmaps, i, j)
    
    sound_distances = phonemes.get_phonetic_distances()

    sound = []
    visual = []

    for key in visual_distances.keys():
        visual.append(visual_distances[key])
        sound.append(sound_distances[key][0])

    nc = np.corrcoef(visual, sound)[0, 1]
    sc = pearsonr(visual, sound)

    print("Correlation (NumPy):", nc)
    print("Correlation (SciPy):", sc)
