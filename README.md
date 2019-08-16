# font-systematicity

This library is intended to aid reserach into optimizing the sound-shape systematicity of fonts. For more information about sound-shape systematicity, see https://psyarxiv.com/n85mb/.

## Getting Started

1. Create a new SQLite database. This command will create \data\results.db, relative to your current directory

```python
python data.py
```

2. Load fonts. You should customize the list of directories at the bottom of this file.

```python
python fonts.py
```

3. Calculate phonological distances. This file contains phoneme vector representations for paradigmatic British English pronunciations. If you are working with another character set, language, or pronunciation definition, you need only to replace the ```phoneme``` dictionary with your own phonological vectors.

```python
python sounds.py
```

## Running experiments

First, define the characters, fonts, and point sizes for your experiments
```python
chars = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u", "v", "w", "y", "z"]
point_sizes = [12, 24, 48, 96]

data.db.connect()
fonts = Font.select().where(Font.is_variable == True)
```

Measure default systematicity:
```python
experiments.default_systematicity(chars, fonts, point_sizes)
```

Search for coordinate that result in better sound-shape systematicity (OpenType font variations only):
```python
experiments.simulated_annealing(chars, fonts, point_sizes, init_temp=.02, time=500)
```

### You can also invoke individual experiment steps directly.

Generate any set of glyphs:

 ``` python
chars = ["耳","目","口","手","足","日","月","水","火","山","石","田","禾","兔","鸟","竹","羊","木","网","刀","尺","心","雨","又","云","女","小","少"]
fonts = Font.select().where(
    (Font.name == "simfang") |
    (Font.name == "simkai")
)

for font in fonts:
    glyph_set_id = systematicity.get_glyphs(chars, font, 96)
```

Measure distances between glyphs:

```python
distances = systematicity.get_shape_distances(glyph_set_id)
```

Calculate sound-shape correlation:
```python
result = get_correlation(glyph_set_id, sound_metric="Euclidean", shape_metric="Hausdorff")
```