import io
import json
import pickle

from peewee import *
from datetime import date

db = SqliteDatabase(r'data\results.db')

class PickleBlobField(BlobField):
    def db_value(self, value):
        return value if value is None else pickle.dumps(value)

    def python_value(self, value):
        return value if value is None else pickle.loads(value)

class BlobStreamField(BlobField):
    def db_value(self, value):
        return value
    
    def python_value(self, value):
        return io.BytesIO(value)

class BaseModel(Model):
    class Meta:
        database = db

class Font(BaseModel):
    name = CharField()
    file_name = CharField()
    font_file = BlobStreamField()
    is_variable = BitField()
    is_serif = BitField()
    axes = CharField(max_length=1000, null=True)

class GlyphSet(BaseModel):
    font = ForeignKeyField(Font, backref='glyph_sets')
    coords = CharField(max_length=1000, null=True)
    size = IntegerField()
    chars = CharField(max_length=1000)    

class Glyph(BaseModel):
    glyph_set = ForeignKeyField(GlyphSet, backref='glyphs')
    character = FixedCharField(max_length=1)
    bitmap = PickleBlobField()

class ShapeDistance(BaseModel):
    glyph1 = ForeignKeyField(Glyph)
    glyph2 = ForeignKeyField(Glyph)
    metric = CharField(max_length=20)
    distance = FloatField()
    points1 = CharField(max_length=100, null=True)
    points2 = CharField(max_length=100, null=True)

class SoundDistance(BaseModel):
    char1 = FixedCharField(max_length=1)
    char2 = FixedCharField(max_length=1)
    metric = CharField(max_length=20)
    distance = FloatField()

class Correlation(BaseModel):
    glyph_set = ForeignKeyField(GlyphSet, backref='correlations')
    shape_metric = CharField()
    sound_metric = CharField()
    r_value = FloatField()
    p_value = FloatField()

def create():
    db.connect()
    db.create_tables([Font, GlyphSet, Glyph, ShapeDistance, SoundDistance, Correlation])
    db.close()

if __name__ == "__main__":
    create()