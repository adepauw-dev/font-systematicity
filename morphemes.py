from typing import NamedTuple
import _ctypes

import freetype
import numpy as np

from ft_structs_mm import FT_MM_VarPtr
from distance import HaussdorffDistance

"""
    Renders monochrome bitmap glyphs and associated metrics using the FreeType
    typography library. Includes support for OpeType font variations.
"""
class GlyphRenderer:
    def __init__(self, fileName):
        self._face = freetype.Face(fileName)

        self._variations = FT_MM_VarPtr()
        freetype.FT_Get_MM_Var(self._face._FT_Face, _ctypes.byref(self._variations))

        self._axes = []
        if self._variations: # NULL pointers have false boolean value
            for i in range(self._variations.contents.num_axis):
                axis = self._variations.contents.axis[i]
                if axis is None:
                    break
                    
                font_axis = FontAxis(
                    axis.name, axis.tag, axis.minimum, axis.maximum)
                self._axes.append(font_axis)
    
    """
        Renders a monochrome characer bitmap using the specified size and optional 
        variable font coordinates.
    """
    def bitmap(self, char, size, coords):
        self.configure_font(size, coords)
        return self.render(char)

    """
        Renders a monochrome characer bitmap using the specified size and 
        optional variable font coordinates.
    """
    def bitmaps(self, chars, size, coords):
        self.configure_font(size, coords)
        
        glpyh_bitmaps = []
        for char in chars:
            glpyh_bitmaps.append(self.render(char))
        
        return self.align_glyphs(glpyh_bitmaps)

    """
        Sets base font configuration, including font size and font variation
        coordinates.
    """
    def configure_font(self, size, coords):
        self._face.set_char_size(size*64)
        
        if coords is not None:
            coords_type = freetype.FT_Fixed * len(coords)
            ft_coords = coords_type(*coords)
            freetype.FT_Set_Var_Design_Coordinates(self._face._FT_Face, len(coords), ft_coords)

    """
        Render glyph bitmap and return with positioning metrics.
    """
    def render(self, char):
        self._face.load_char(char, freetype.FT_LOAD_RENDER | freetype.FT_LOAD_TARGET_MONO)
        metrics = self._face.glyph.metrics
        bitmap = self._face.glyph.bitmap

        data = []
        for i in range(bitmap.rows):
            row = []
            for j in range(bitmap.pitch):
                row.extend(self.pixels_to_list(bitmap.buffer[i*bitmap.pitch+j]))
            data.extend(row[:bitmap.width])
        
        return GlyphBitmap(
            bitmap = np.array(data).reshape(bitmap.rows, bitmap.width),
            height = int(metrics.height/64), 
            width = int(metrics.width/64),
            y_bearing = int(metrics.horiBearingY/64), 
            x_bearing = int(metrics.horiBearingX)/64)      

    """
        Converts monochrome pixel values from a byte of bits to a list of ints.
    """
    def pixels_to_list(self, byte):
        pixels = []
        for i in range(8):
            # Add "white" pixel (1) if least-significant bit is 0
            pixels.insert(0, int((byte & 1) != 1))
            # Shift bits one place right
            byte = byte >> 1
        return pixels

    """
        Modifies the bitmaps in order to align the associated glyphs within
        a common pixel grid so that shape distances can be accurately compared.

        Horizontal alignment is centered and vertical alignment is fixed to 
        a common guideline.
    """
    def align_glyphs(self, glyph_bitmaps):
        # Height above of the guideline will be the maximum Y bearing
        max_ascent = max([g.y_bearing for g in glyph_bitmaps])
        
        # Depth below the guideline will be the max difference between the height and Y bearing
        max_descent = max([g.height - g.y_bearing for g in glyph_bitmaps])
        
        # Width of bitmap  
        max_width = max([g.width for g in glyph_bitmaps])
        
        bitmaps = []
        for glyph in glyph_bitmaps:
            bitmap = glyph.bitmap
            ascent_needed = max_ascent - glyph.y_bearing            
            descent_needed = max_descent - (bitmap.shape[0] - glyph.y_bearing)

            if (ascent_needed > 0):
                bitmap = np.concatenate((np.ones((ascent_needed, bitmap.shape[1])), bitmap), axis=0)
            if (descent_needed > 0):
                bitmap = np.concatenate((bitmap, np.ones((descent_needed, bitmap.shape[1]))), axis=0)

            cols_needed = max_width - bitmap.shape[1]
            cols_add_left = np.ones((bitmap.shape[0], int(cols_needed/2)))
            cols_add_right = np.ones((bitmap.shape[0], cols_needed - int(cols_needed/2)))

            bitmap = np.concatenate((cols_add_left, bitmap), axis=1)
            bitmap = np.concatenate((bitmap, cols_add_right), axis=1)
            
            bitmaps.append(bitmap)
        
        return bitmaps

class FontAxis(NamedTuple):
    """Class to represent a font variation axis. """
    name: str
    tag: str
    minimum: int
    maximum: int

class GlyphBitmap(NamedTuple):
    """Class to represent a rasterized glpyh and its metrics. """
    bitmap: np.ndarray
    height: int
    width: int
    y_bearing: int
    x_bearing: int

def hausdorff_distance(bitmap1, bitmap2):
    # Transform bitmaps into points
    points1 = get_points(bitmap1)
    points2 = get_points(bitmap2)
    
    hauss = HaussdorffDistance.get_distance(points1, points2)
    
    # Return haussdorff distancs and the contributing point coordinates
    return ((hauss[0][0], points1[hauss[0][1]], points2[hauss[0][2]]), (hauss[1][0], points2[hauss[1][1]], points1[hauss[1][2]]))
    
def get_points(bitmap):
    points = []
    for i in range(bitmap.shape[0]):
        for j in range(bitmap.shape[1]):
            if bitmap[i][j] == 0:
                points.append((i,j))
    return points