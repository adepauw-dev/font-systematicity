-- Delete duplicate experiment glyph set records
-- Deletes one duplicate per run
-- These were created due to a bug in glyph reuse code
delete from experimentglyphset where id in 
(
	select id from experimentglyphset
	group by experiment_id, glyph_set_id
	having count(1) > 1 and MAX(id)
	order by id desc;
)

-- Check for duplicates
select id, experiment_id, glyph_set_id, count(1) from experimentglyphset
	group by experiment_id, glyph_set_id
	having count(1) > 1 and MIN(id)
	order by count(1) desc;