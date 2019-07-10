select sd.id, g1.id, g2.id, g1.character, g2.character, sd.distance, sd.points1, sd.points2 
from shapedistance sd
	inner join glyph g1 on sd.glyph1_id = g1.id
	inner join glyph g2 on sd.glyph2_id = g2.id
	inner join glyphset gs on g1.glyph_set_id = gs.id
where gs.id = 83491
order by distance desc
	
select distance, count(1)
from shapedistance sd
	inner join glyph g1 on sd.glyph1_id = g1.id
	inner join glyph g2 on sd.glyph2_id = g2.id
	inner join glyphset gs on g1.glyph_set_id = gs.id
where gs.id = 83489
group by distance
order by count(1) desc

select sd.id, g1.id, g2.id, g1.character, g2.character, sd.distance, sd.points1, sd.points2 
from shapedistance sd
	inner join glyph g1 on sd.glyph1_id = g1.id
	inner join glyph g2 on sd.glyph2_id = g2.id
	inner join glyphset gs on g1.glyph_set_id = gs.id
where gs.id = 83491
order by distance desc

select * from glyphset where id = 83489
295
select * from font where id = 368