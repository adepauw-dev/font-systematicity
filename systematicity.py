import io
from itertools import combinations
import json
from typing import NamedTuple

import numpy as np
from scipy.stats.stats import pearsonr
from peewee import DoesNotExist

import data
from data import Font, GlyphSet, Glyph, SoundDistance, ShapeDistance, Correlation
import shapes

"""
    Delete any glyph sets that match the specified criteria. All glyphs, shapedistances,
    and correlations will be deleted as well.
"""
def delete_glyph_set(chars, font, size, coords=None):
    coords_serial = json.dumps(coords)
    chars_serial = json.dumps(chars)

    with data.db.atomic():
        glyph_sets = (GlyphSet
                    .select()
                    .where(
                        GlyphSet.font_id == font.id, 
                        GlyphSet.size == size,
                        GlyphSet.coords == coords_serial, 
                        GlyphSet.chars == chars_serial))
        print("Found {0} matching glyph sets".format(len(glyph_sets)))

        for glyph_set in glyph_sets:
            print("Deleting glyph set {0}".format(glyph_set.id))
            result = glyph_set.delete_instance(recursive=True)
            print(result, "glyph sets deleted")

"""
    Gets or creates a set of glyphs using the specified criteria. If a glyph set for this
    criteria already exists, the glyphset id is loaded and returned. If a set does not
    exist, a new glyphset is created and glyphs are rendered and saved.
"""
def get_glyphs(chars, font, size, coords=None):
    coords_serial = None if (coords is None or len(coords) == 0) else json.dumps(coords)
    chars_serial = json.dumps(chars)
    
    # Check if glyphs already exist    
    glyph_sets = (GlyphSet
                    .select()
                    .where(
                        GlyphSet.font_id == font.id, 
                        GlyphSet.size == size,
                        GlyphSet.coords == coords_serial, 
                        GlyphSet.chars == chars_serial)
                    .execute())
    if len(glyph_sets) > 0:
        return glyph_sets[0].id

    renderer = shapes.GlyphRenderer(io.BytesIO(font.font_file))
    bitmaps = renderer.bitmaps(chars, size, coords)

    glyph_set = GlyphSet(font=font, size=size, coords=coords_serial, chars=chars_serial)
    glyph_set.save()
    
    glyphs = []
    for i in range(len(chars)):
        glyph = Glyph(
            glyph_set_id = glyph_set.id,
            character = chars[i],
            bitmap = bitmaps[i]
        )
        glyphs.append(glyph)

    with data.db.atomic():
        Glyph.bulk_create(glyphs, batch_size=100)

    return glyph_set.id

"""
    Calculate all visual distance measures between all possible combinations
    of glyphs belonging to the specified set. If the calculations already 
    exist, the existing records are returned.
"""
def get_and_save_shape_distances(glyph_set_id):
    glyph_query = Glyph.select().where(Glyph.glyph_set_id == glyph_set_id)
    glyphs = [glyph for glyph in glyph_query]

    # Get existing glyph distances
    Glyph1 = Glyph.alias()
    Glyph2 = Glyph.alias()

    shape_query = (ShapeDistance
                    .select()
                    .join(Glyph1, on=ShapeDistance.glyph1)
                    .switch(ShapeDistance)
                    .join(Glyph2, on=ShapeDistance.glyph2)
                    .where(
                        (Glyph1.glyph_set_id == glyph_set_id) &
                        (Glyph2.glyph_set_id == glyph_set_id)))
    if len(shape_query) > 0:
        # distances already calculated, return existing values
        return [s for s in shape_query]

    shape_distances = get_shape_distances(glyphs)
    
    with data.db.atomic():
        ShapeDistance.bulk_create(shape_distances, batch_size=100)
    
    return shape_distances

def get_shape_distances(glyphs):
    shape_distances = []

    # Generate all pairs of chars and calculate distance
    pairs = list(combinations(range(len(glyphs)),2))
    for pair in pairs:
        i = pair[0]
        j = pair[1]
        
        glyph_1 = glyphs[i]
        glyph_2 = glyphs[j]
        bitmap_1 = glyph_1.bitmap
        bitmap_2 = glyph_2.bitmap

        haus = shapes.hausdorff_distance(bitmap_1, bitmap_2)

        if haus is None:
            raise FailedRenderException("Unable to determine distance and correlation because at least one glyph failed to render.")

        contrib_points1 = json.dumps([haus[0][1], haus[1][2]])
        contrib_points2 = json.dumps([haus[0][2], haus[1][1]])
        
        s = ShapeDistance(
            glyph1 = glyph_1.id, 
            glyph2 = glyph_2.id, 
            metric = "hausdorff",
            distance = max(haus[0][0], haus[1][0]),
            points1 = contrib_points1,
            points2 = contrib_points2
        )

        shape_distances.append(s)
    
    return shape_distances

"""
    Calculate correlation between the sound and shape distances for the 
    specified glyph set, using the distance metric specified. If the 
    correlation has already been calculated, the existing results are 
    returned.
"""
def get_correlation(glyph_set_id, sound_metric, shape_metric):
    # Fetch from db if it's already calculated
    query = (Correlation
                    .select()
                    .where(
                        (Correlation.glyph_set_id == glyph_set_id) & 
                        (Correlation.sound_metric == sound_metric) & 
                        (Correlation.shape_metric == shape_metric)))
    if len(query) > 0:
        return query.first()

    sound_query = (SoundDistance
                    .select()
                    .where(SoundDistance.metric == sound_metric)
                    .order_by(SoundDistance.char1, SoundDistance.char2))
    
    Glyph1 = Glyph.alias()
    Glyph2 = Glyph.alias()
    shape_query = (ShapeDistance
                    .select()
                    .join(Glyph1, on=ShapeDistance.glyph1)
                    .switch(ShapeDistance)
                    .join(Glyph2, on=ShapeDistance.glyph2)
                    .where(
                        (Glyph1.glyph_set_id == glyph_set_id) &
                        (Glyph2.glyph_set_id == glyph_set_id) &
                        (ShapeDistance.metric == shape_metric))
                    .order_by(Glyph1.character, Glyph2.character))

    sound_distances = [s.distance for s in sound_query]
    shape_distances = [s.distance for s in shape_query]

    if (len(sound_distances) != len(shape_distances)):
        raise Exception("Numer of shape ({0}) and sound ({1}) distances are not equal for glyph set {2}, sound metric {3}, shape metric {4}".format(
            len(shape_distances), len(sound_distances), glyph_set_id, sound_metric, shape_metric))
    
    if np.std(shape_distances) == 0:
        raise Exception("Unable to calculate correlation for glyph set {0}: standard deviation of shape distances is zero."
            .format(glyph_set_id))
    
    corr_value = pearsonr(shape_distances, sound_distances)

    correlation = Correlation(
        glyph_set = glyph_set_id,
        shape_metric = shape_metric,
        sound_metric = sound_metric,
        r_value = corr_value[0],
        p_value = corr_value[1]
    )
    correlation.save()

    return correlation

"""
    Perform a complete  measurement of systematiciy for the font, characters,
    size, and variation coordinates specified. Renders and saves a set of glyphs,
    measures their visual distances, and calculates the correlation between their
    visual (shape) and phonological (sound) distances, using a variety of measures.

    This method returns only the correlation using the Edit distance.
"""
def evaluate(chars, font, font_size, coords=None, overwrite=False):
    if (overwrite):
        delete_glyph_set(chars, font, font_size, coords)
    
    glyph_set_id = get_glyphs(chars, font, font_size, coords)

    get_and_save_shape_distances(glyph_set_id)

    euclidean_corr = get_correlation(glyph_set_id, "Euclidean", "hausdorff")
    edit_sum_corr = get_correlation(glyph_set_id, "Edit_Sum", "hausdorff")
    edit_corr = get_correlation(glyph_set_id, "Edit", "hausdorff")
    
    return SystematicityResult(
        glyph_set_id = glyph_set_id,
        edit_correlation = edit_corr.r_value,
        edit_sum_correlation = edit_sum_corr.r_value,
        euclidean_correlation = euclidean_corr.r_value
    )

class SystematicityResult(NamedTuple):
    """Class to represent the results of a systematiciy evaluation. """
    glyph_set_id: int
    edit_correlation: float
    edit_sum_correlation: float
    euclidean_correlation: float

class FailedRenderException(Exception):
    """Exception for when a glyph renders with no pixels"""
    pass
