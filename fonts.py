import io
import json
import os
from pathlib import Path

import data
import shapes

"""
    Load all fonts from a specified directory into the data store for 
    rendering and analysis. Only OpenType (*.otf) and TrueType (*.ttf) fonts
    are supported. 
"""

def load_fonts(font_dir):
    # Only use OpenType and TrueType font files
    font_files = [_ for _ in Path(font_dir).glob("**/*.otf")]
    font_files += [_ for _ in Path(font_dir).glob("**/*.ttf")]

    data.db.connect()
    for file_path in font_files:
        print("Importing {0}".format(file_path))
        file_name = os.path.basename(file_path)
        font_name = os.path.splitext(file_name)[0]
        
        with open(os.path.join(file_path), mode='rb') as font_file:
            font_blob = font_file.read()
            font = data.Font(name=font_name, file_name=file_name, font_file=font_blob)

            file_stream = io.BytesIO(font_blob)
            
            # Add data for OpenType variation fonts
            renderer = shapes.GlyphRenderer(file_stream)
            if len(renderer._axes) > 0:
                axes = []
                for axis in renderer._axes:
                    obj = {
                        'name': axis.name, 
                        'default':axis.default,
                        'minimum':axis.minimum,
                        'maximum':axis.maximum
                    }
                    axes.append(obj)                
                
                font.is_variable = True
                font.axes = json.dumps({"axes":axes})

            font.save()

    data.db.close()

if __name__ == "__main__":
    load_fonts(r"C:\Windows\Fonts")
    load_fonts(r"data\variable-fonts")