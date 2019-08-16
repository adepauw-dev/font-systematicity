import io
import json
import random
from collections import defaultdict

import data
from data import Font, GlyphSet, Glyph, SoundDistance, ShapeDistance, Correlation
import experiments
import shapes
import systematicity
import visualization

import matplotlib.backends.backend_pdf
import matplotlib.pyplot as plt

def render_hausdorff_distance(shape_distance_id):
    Glyph1 = Glyph.alias()
    Glyph2 = Glyph.alias()
    query = (ShapeDistance
                    .select()
                    .join(Glyph1, on=ShapeDistance.glyph1)
                    .switch(ShapeDistance)
                    .join(Glyph2, on=ShapeDistance.glyph2)
                    .where(
                        ShapeDistance.id == shape_distance_id))
    result = query[0]
    points1 = json.loads(result.points1)
    points2 = json.loads(result.points2)
    bitmap1 = result.glyph1.bitmap
    bitmap2 = result.glyph2.bitmap
    
    bitmap = visualization.render_distance_overlay(
        result.glyph1.character, 
        result.glyph2.character, 
        bitmap1,
        bitmap2,
        points1,
        points2,
        result.distance,
        result.distance)
    
    return bitmap

def show_hausdorff_distance(shape_distance_id):
    bitmap = render_hausdorff_distance(shape_distance_id)
    visualization.show_image(bitmap)

def save_hausdorf_distances(shape_distance_ids):
    pdf = matplotlib.backends.backend_pdf.PdfPages("output.pdf")
    for shape_distance_id in shape_distance_ids:
        bitmap = render_hausdorff_distance(shape_distance_id)
        plt.axis("off")
        plt.imshow(bitmap, interpolation="nearest", cmap=plt.cm.gray, origin="upper")
        pdf.savefig()
    pdf.close()

def get_chinese_distances():
    chars = ["耳","目","口","手","足","日","月","水","火","山","石","田","禾","兔","鸟","竹","羊","木","网","刀","尺","心","雨","又","云","女","小","少"]
    fonts = Font.select().where(
        (Font.name == "simfang") |
        (Font.name == "simkai")
    )
    
    for font in fonts:
        renderer = shapes.GlyphRenderer(io.BytesIO(font.font_file))
        glyph_set_id = systematicity.get_glyphs(chars, font, 96)
        distances = systematicity.get_shape_distances(glyph_set_id)

def axes_analysis():
    fonts = Font.select().where(
        (Font.is_variable == True)
    )
    axis_count = defaultdict(int)
    axis_sum = defaultdict(int)
    
    for font in fonts:
        axes = json.loads(font.axes)["axes"]
        axis_sum[len(axes)] += 1

        for axis in axes:
            axis_count[axis["name"]] += 1
        
    print(axis_count)
    print(axis_sum)    

if __name__ == "__main__":   
    chars = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u", "v", "w", "y", "z"]
    data.db.connect()

    fonts = Font.select().where(Font.is_variable == True)
    
    # # """ Calculate systematicity of fonts using default coordinates """
    # experiments.default_systematicity(chars, fonts, [12])
   
    # """  Run an experiment using simulated annealing to minimize """ 
    #experiments.simulated_annealing(chars, fonts, [24], .02, 500, "gaussian", 0.1, method=experiments.ExperimentType.SimulatedAnnealingMin)
    
    # """  Run an experiment using simulated annealing """ 
    # experiments.simulated_annealing(chars, fonts, [12, 24], .02, 500)
