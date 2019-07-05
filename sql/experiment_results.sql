select max(c.r_value), e.id, e.name
from experiment e
	inner join experimentglyphset egs on e.id = egs.experiment_id
	inner join glyphset gs on egs.glyph_set_id = gs.id
	inner join correlation c on c.glyph_set_id = gs.id
	inner join font f on gs.font_id = f.id
where e.end_time not null
	and e.id >= 23
group by e.id, e.name