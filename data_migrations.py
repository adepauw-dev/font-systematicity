from peewee import CharField, SqliteDatabase
from playhouse.migrate import SqliteMigrator, migrate

"""
    Data migrations - for users of earlier version.
    Data.py is kept up-to-date with these changes and they
    are irrelevant after use and for new users.
"""

def apply_v2():
    db = SqliteDatabase(r"data\results.db")
    migrator = SqliteMigrator(db)
    
    points1 = CharField(max_length=100, null=True)
    points2 = CharField(max_length=100, null=True)
        
    migrate(
        migrator.add_column("shapedistance", "points1", points1),
        migrator.add_column("shapedistance", "points2", points2),
        migrator.drop_column("shapedistance", "bitmap"),
    )

def apply_v3():
    db = SqliteDatabase(r"data\results.db")
    migrator = SqliteMigrator(db)

    migrate(
        migrator.rename_column("sounddistance", "char_1", "char1"),
        migrator.rename_column("sounddistance", "char_2", "char2")
    )

if __name__ == "__main__":
    apply_v3()
