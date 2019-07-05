import json

import data
from data import Font, GlyphSet, Glyph, SoundDistance, ShapeDistance, Correlation
import experiments
import systematicity
import visualization
        
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
    #visualization.save_image(bitmap, "{0}{1}".format(chars[i], chars[j]), path=path)

if __name__ == "__main__":
    chars = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u", "v", "w", "y", "z"]
    
    data.db.connect()
    fonts = Font.select().where(Font.is_variable == True)
    #fonts = Font.select().where(Font.name == "VotoSerifGX")

    # Run an experiment using random search
    experiments.random_search(chars, fonts, [12, 24], 250)
    
    # Run an experiment using simulated annealing
    experiments.simulated_annealing(chars, fonts, [12, 24], .02, 250)
    
    # # Run an experiment using grid search
    # experiments.grid_search(chars, fonts, [12, 24], 5)
    
    # """ Evaluate a font, overwriting data """
    # systematicity.evaluate(chars, fonts[0], 96, None, True)
    
    # """ Generate an image illustrating the hausdorff image of the first two glyphs in a glyph set """
    # print_hausdorff_distance(388)