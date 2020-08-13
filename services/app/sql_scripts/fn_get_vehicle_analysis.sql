create or replace function fn_get_vehicle_analysis(search_value text) returns json
	language plpgsql
as 
$$
declare 
	var_result_to_render json;
begin 
	select 
		result_to_render
	into 
		var_result_to_render
	from 
		rides_analysis
	where 
		vehicle_id = search_value or qr_code = search_value;
	
	return var_result_to_render;
end
$$