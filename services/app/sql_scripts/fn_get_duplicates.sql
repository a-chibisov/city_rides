create or replace function fn_get_duplicates() returns json
	language plpgsql
as 
$$
declare 
	var_result_to_render json;
begin 
	select json_agg(dl) into var_result_to_render from duplicate_log as dl;
	
	return var_result_to_render;
end
$$