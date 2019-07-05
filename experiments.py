import io
import math
import random

import data
from data import Font
import shapes
import systematicity

"""
    Evaluate the systematicity in sound-shape correlation for a set of fonts
    and font sizes. For variable fonts, evalutes default coordinate values
    only.
"""
def evaluate_fonts(chars, fonts, font_sizes):
    for font in fonts:
        for font_size in font_sizes:
            systematicity.evaluate(chars, font, font_size, None)

"""
    Generates a set number of evenly spaced points in the specified space.
"""
def get_grid_coords(minimum, maximum, points):
    if points < 2:
        raise Exception("Points must be greater than or equal to 2")
    if minimum > maximum:
        raise Exception("Minimum must be less than or equal maximum")
        
    interval = (maximum - minimum) / (points - 1)
    return [int(interval * i + minimum) for i in range(points)]

"""
    Generates the number of randomly selected points for the specified
    font axes.
"""
def get_random_coords(axes, num_points):
    points = []
    for i in range(num_points):
        coords = []
        for axis in axes:
            coords.append(random.uniform(axis.minimum, axis.maximum))
        points.append(coords)
    return points

"""
    Get best systematiciy performing a grid search over the possible values of
    each individual axis. Modifies only a single axis at a time: all other axes
    are set to their default values.
"""
def grid_search(chars, fonts, font_sizes, grid_count):
    for font in fonts:
        for font_size in font_sizes:
            renderer = shapes.GlyphRenderer(font.font_file)
            
            defaults = [axis.default for axis in renderer._axes]
            for index in range(len(renderer._axes)):
                axis = renderer._axes[index]
                
                vals = get_grid_coords(axis.minimum, axis.maximum, grid_count)
                
                for idx, val in enumerate(vals):
                    coords = defaults.copy()
                    coords[index] = val
                    
                    print("Calculating {0} pt {1} for {2} value of {3}...".format(font_size, font.name, axis.name, val))
                    systematicity.evaluate(chars, font, font_size, coords)

"""
    Perform a random search over the possible values of each font's axes.
    Generates num_points candidates.
"""
def random_search(chars, fonts, font_sizes, num_points):
    for font in fonts:
        for font_size in font_sizes:
            renderer = shapes.GlyphRenderer(font.font_file)

            points = get_random_coords(renderer._axes, num_points)
            # Include min and max
            points.insert(0, [axis.minimum for axis in renderer._axes])
            points.append([axis.maximum for axis in renderer._axes])

            for point in points:
                print("Calculating {0} pt {1} with coords {2}...".format(font_size, font.name, point))
                systematicity.evaluate(chars, font, font_size, point)

"""
   Simulated annealing algorithm for finding optimal coordinates. 
"""
def simulated_annealing(chars, fonts, font_sizes, initial_temperature, time):
    for font in fonts:
        for font_size in font_sizes:
            print("Experiment: font {0} size {1}".format(font.name, font_size))
            temperature = initial_temperature
            renderer = shapes.GlyphRenderer(io.BytesIO(font.font_file))
            candidate = get_random_coords(renderer._axes, 1)

            result = systematicity.evaluate(chars, font, font_size, candidate)
            iteration = 1
            
            best_candidate = candidate
            best_result = result
            best_iteration = iteration

            print("Staring at {0}, {1}".format(best_candidate, best_result))

            while iteration < time and temperature > 0:
                new_candidate = convolve_gaussian(candidate, renderer._axes, .05)
                new_result = systematicity.evaluate(chars, font, font_size, new_candidate)
                
                p = random.uniform(0.0, 1.0)
                if new_result > result or math.exp((new_result - result)/temperature) > p:
                    print("{0:3d} MOVE: {1:.4f}, {2:.4f} > {3:.4f}, temp: {4:.4f}, {5}".format(iteration, new_result, math.exp((new_result - result)/temperature), p, temperature, new_candidate))
                    
                    candidate = new_candidate
                    result = new_result                    
                else:
                    print("{0:3d} STAY: {1:.4f}, {2:.4f} <= {3:.4f}, temp: {4:.4f}, {5}".format(iteration, new_result, math.exp((new_result - result)/temperature), p, temperature, new_candidate))

                if result > best_result:                    
                    best_result = result
                    best_candidate = candidate
                    best_iteration = iteration

                iteration += 1
                temperature = initial_temperature * (1 - iteration/time)
    
            print("Best candidate for {0} size {1} in iteration {2}: {3:.4f}, {4}".format(font.name, font_size, best_iteration, best_result, best_candidate))

"""
    Randomly convolve the set of axis coordinates uniformly bounded by the 
    +/- percent of possible range defined by step_range.
"""
def convolve_uniform(coords, axes, step_range):
    if step_range > 1 or step_range <= 0:
        raise Exception("Invalid step_range: {0}. Should be 0 < step_range <= 1.".format(step_range))

    new_coords = []
    
    for i in range(len(axes)):
        axis = axes[i]
        coord = coords[i]

        axis_range = axis.maximum - axis.minimum
        conv_range = (axis_range * step_range)
        
        while True:
            new_coord = coord + random.uniform(-conv_range, conv_range)
            if new_coord >= axis.minimum and new_coord <= axis.maximum:
                break

        new_coords.append(new_coord)

    return new_coords

"""
    Randomly convolve the set of axis coordinates within the applicable range
    using a Gaussian distribution having zero mean. The variance will be set
    to the portion of the axis range specified by var_range. For example, a
    var_range of 0.01 for axes with ranges of [20, 80, 100] will yield 
    variances of [0.2, 0.8, 1].
"""
def convolve_gaussian(coords, axes, var_range):
    if var_range <= 0:
        raise Exception("Invalid var_range: {0}. var_range should be > 0"
            .format(var_range))
    if var_range > 1:
        raise Warning("Unusally high var_range of {0} will result in many "
                        "rejected convolutions outside the axis range."
                        .format(var_range))
    new_coords = []
    
    for i in range(len(axes)):
        axis = axes[i]
        coord = coords[i]
        
        axis_range = axis.maximum - axis.minimum
        variance = axis_range * var_range
        
        while True:
            new_coord = coord + random.gauss(0, variance)
            if new_coord >= axis.minimum and new_coord <= axis.maximum:
                break

        new_coords.append(new_coord)

    return new_coords

if __name__ == "__main__":
    font = Font.select().where(Font.name == 'amstelvar-roman').first()
    renderer = shapes.GlyphRenderer(font.font_file)


    ### CONVOLVE TESTING

    # coords = []
    # for axis in renderer._axes:
    #     print(axis.name, axis.minimum, axis.maximum)
    #     coords.append(axis.default)
    # print(coords)

    # step_range = 1
    # for i in range(100):
    #     # coords = convolve_uniform(coords, renderer._axes, step_range)    
    #     coords = convolve_gaussian(coords, renderer._axes, 0.10)
    #     print(coords)