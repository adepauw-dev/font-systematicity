"""
    These types are wrappers to FreeType structs not currently supported
    in freetype-py as of v2.1.0.post1. Code conventions for this file follow
    those of freetype-py for possible inclusion in future PR.

    Structs are documented at
    https://www.freetype.org/freetype2/docs/reference/ft2-multiple_masters.html
"""
from freetype.ft_types import FT_Fixed, FT_String_p, FT_UInt, FT_ULong, POINTER, Structure

# ----------------------------------------------------------------------------
# A structure to model a named instance in a TrueType GX or OpenType variation 
# font.
#
# This structure can't be used for Adobe MM fonts.
class FT_Var_Named_Style(Structure):
    '''
    A structure to model a named instance in a TrueType GX or OpenType 
    variation font.

    This structure can't be used for Adobe MM fonts.

    coords: The design coordinates for this instance. This is an array with one 
    entry for each axis.

    strid: The entry in ‘name’ table identifying this instance.

    psid: The entry in ‘name’ table identifying a PostScript name for this 
    instance. Value 0xFFFF indicates a missing entry.
    '''
    _fields_ = [
        ('coords',      POINTER(FT_Fixed)),
        ('strid',       FT_UInt),
        ('psid',        FT_UInt) ]

# ----------------------------------------------------------------------------
# A structure to model a given axis in design space for Multiple Masters, 
# TrueType GX, and OpenType variation fonts.
class FT_Var_Axis(Structure):
    '''
    A structure to model a given axis in design space for Multiple Masters, 
    TrueType GX, and OpenType variation fonts.

    name: The axis's name. Not always meaningful for TrueType GX or OpenType 
    variation fonts.

    minimum: The axis's minimum design coordinate.

    def: The axis's default design coordinate. FreeType computes meaningful 
        default values for Adobe MM fonts.

    maximum: The axis's maximum design coordinate.

    tag: The axis's tag (the equivalent to ‘name’ for TrueType GX and OpenType 
    variation fonts). FreeType provides default values for Adobe MM fonts if 
    possible.

    strid: The axis name entry in the font's ‘name’ table. This is another (and 
    often better) version of the ‘name’ field for TrueType GX or OpenType 
    variation fonts. Not meaningful for Adobe MM fonts.
    '''
    _fields_ = [
        ('name',        FT_String_p),
        ('minimum',     FT_Fixed),
        ('def',         FT_Fixed),
        ('maximum',     FT_Fixed),
        ('tag',         FT_ULong),
        ('strid',       FT_UInt) ]

# ----------------------------------------------------------------------------
# A structure to model the axes and space of an Adobe MM, TrueType GX, or 
# OpenType variation font.
#
# Some fields are specific to one format and not to the others.
class FT_MM_Var(Structure):
    '''
    A structure to model the axes and space of an Adobe MM, TrueType GX, or 
    OpenType variation font.

    Some fields are specific to one format and not to the others.
    '''
    _fields_ = [
        ('num_axis',        FT_UInt),
        ('num_designs',     FT_UInt),
        ('num_namedstyles', FT_UInt),
        ('axis',            POINTER(FT_Var_Axis)),
        ('namedstyle',      POINTER(FT_Var_Named_Style)) ]

FT_MM_VarPtr = POINTER(FT_MM_Var)