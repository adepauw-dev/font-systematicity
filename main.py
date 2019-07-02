import io
import json
import os
import random
import sys
from itertools import combinations

import numpy as np
from scipy.stats.stats import pearsonr
import matplotlib.pyplot as plt
from peewee import DoesNotExist

import data
from data import Font, GlyphSet, Glyph, SoundDistance, ShapeDistance, Correlation
import shapes
import sounds
import systematicity
import visualization


def get_grid_coords(minimum, maximum, points):
    if points < 2:
        raise Exception("Points must be greater than or equal to 2")
    if minimum > maximum:
        raise Exception("Minimum must be less than or equal maximum")
        
    interval = (maximum - minimum) / (points - 1)
    return [int(interval * i + minimum) for i in range(points)]

def get_random_coords(axes, num_points):
    points = []
    points.append([axis.minimum for axis in axes])
    
    for i in range(num_points):
        coords = []
        for axis in axes:
            coords.append(random.randint(axis.minimum, axis.maximum+1))
        points.append(coords)
    points.append([axis.maximum for axis in axes])
    return points

def evaluate_fonts(chars):
    fonts = Font.select()
    for font in fonts:
        for font_size in [12, 24, 48, 96]:
            systematicity.evaluate(chars, font, font_size, None)

def grid_search(chars, fonts, font_sizes, grid_count):
    for font in fonts:
        for font_size in font_sizes:
            renderer = shapes.GlyphRenderer(io.BytesIO(font.font_file))
            
            defaults = [axis.default for axis in renderer._axes]
            for index in range(len(renderer._axes)):
                axis = renderer._axes[index]
                
                vals = get_grid_coords(axis.minimum, axis.maximum, grid_count)
                
                for idx, val in enumerate(vals):
                    coords = defaults.copy()
                    coords[index] = val
                    
                    print("Calculating {0} pt {1} for {2} value of {3}...".format(font_size, font.name, axis.name, val))
                    systematicity.evaluate(chars, font, font_size, coords)

def random_search(chars, fonts, font_sizes, num_points):
    for font in fonts:
        for font_size in font_sizes:
            renderer = shapes.GlyphRenderer(io.BytesIO(font.font_file))
            points = get_random_coords(renderer._axes, num_points)
            for point in points:
                print("Calculating {0} pt {1} with coords {2}...".format(font_size, font.name, point))
                systematicity.evaluate(chars, font, font_size, point)
        
def print_hausdorff_distance(glyph_set_id):
    Glyph1 = Glyph.alias()
    Glyph2 = Glyph.alias()
    query = (ShapeDistance
                    .select()
                    .join(Glyph1, on=ShapeDistance.glyph1)
                    .switch(ShapeDistance)
                    .join(Glyph2, on=ShapeDistance.glyph2)
                    .where(
                        (Glyph1.glyph_set_id == glyph_set_id) &
                        (Glyph2.glyph_set_id == glyph_set_id) &
                        (ShapeDistance.metric == "hausdorff"))
                    .order_by(Glyph1.character, Glyph2.character))

    result = query[0]
    points1 = json.loads(result.points1)
    points2 = json.loads(result.points2)
    bitmap1 = result.glyph1.bitmap
    bitmap2 = result.glyph2.bitmap
    
    print(bitmap1)
    print(type(bitmap1))
    print(bitmap1.shape)
    print(bitmap1[points1[0][0], points1[0][1]])
    print(bitmap1[points1[1][0], points1[1][1]])

    bitmap = visualization.render_image_pair(
        result.glyph1.character, 
        result.glyph2.character, 
        bitmap1,
        bitmap2,
        points1,
        points2,
        result.distance,
        result.distance)

    visualization.show_image(bitmap)
    visualization.save_image(bitmap, "{0}{1}".format(chars[i], chars[j]), path=path)

if __name__ == "__main__":
    chars = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u", "v", "w", "y", "z"]
    
    data.db.connect()
    fonts = Font.select().where(Font.id == 7)
    
    """ Evaluate a font, overwriting data """
    systematicity.evaluate(chars, fonts[0], 96, None, True)
    
    """ Perform a random search for optimal coordinates of a variable font """
    random_search(chars, fonts, [12], 100)
    
    """ Generate an image illustrating the hausdorff image of the first two glyphs in a glyph set """
    print_hausdorff_distance(388)