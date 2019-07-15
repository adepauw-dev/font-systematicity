select * from experiment where id not in (select experiment_id from experimentglyphset);

delete from experimentglyphset where glyph_set_id = 83498;
delete from experiment where id in (select experiment_id from experimentglyphset where glyph_set_id = 83498);
delete from correlation where glyph_set_id = 83498;
delete from shapedistance where glyph1_id in (select id from glyph where glyph_set_id = 83498);
delete from glyph where glyph_set_id = 83498;
delete from glyphset where id = 83498;