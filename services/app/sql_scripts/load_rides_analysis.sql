truncate table rides_analysis;

--note: only completed (i.e. picked-up) deployments are included
insert into rides_analysis
(
	vehicle_id,
	qr_code,
	result_to_render
)
with deployment_pickup_cycles as 
(
	select 
		deployment_id,
		pickup_id,
		vehicle_id,
		qr_code,
		cycle_start_time,
		cycle_end_time
	from 
		(
			select 
				d.task_id as deployment_id,
				p.task_id as pickup_id,
				d.vehicle_id,
				p.qr_code,
				d.time_task_resolved as cycle_start_time,
				p.time_task_created as cycle_end_time,
				row_number() over (partition by d.vehicle_id, d.time_task_resolved order by p.time_task_created asc) as rn
			from 
				deployments as d 
				left join pickups as p 
					on d.vehicle_id = p.vehicle_id 
					and p.time_task_created > d.time_task_resolved 
			where 
				p.time_task_created is not null
		) as q 
	where 
		q.rn = 1
),
most_recent_deployments as 
(
	select 
		deployment_id,
		pickup_id,
		vehicle_id,
		qr_code,
		cycle_start_time,
		cycle_end_time,
		row_number() over (partition by vehicle_id order by cycle_start_time desc) as most_recent_deployment
	from 
		deployment_pickup_cycles
),
recent_rides as 
(
	select 
		mrd.deployment_id,
		mrd.pickup_id,
		mrd.vehicle_id,
		mrd.qr_code,
		mrd.cycle_start_time,
		mrd.cycle_end_time,
		mrd.most_recent_deployment,
		r.time_ride_start,
		r.time_ride_end,
		r.gross_amount,
		r.start_lat,
		r.end_lat,
		r.start_lat,
		r.end_lng,
		fn_calculate_distance(r.start_lat, r.start_lng, r.end_lat, r.end_lng, 'K') as distance,
		'(' || r.start_lat || ', ' || r.start_lng || ')' as start_point,
		'(' || r.end_lat || ', ' || r.end_lng || ')' as end_point
	from 
		most_recent_deployments as mrd 
		left join rides as r 
			on mrd.vehicle_id = r.vehicle_id 
			and (r.time_ride_start >= mrd.cycle_start_time and r.time_ride_start < mrd.cycle_end_time)
			and (r.time_ride_end >= mrd.cycle_start_time and r.time_ride_end < mrd.cycle_end_time)
),
latest_5_rides as 
(
	select 
		deployment_id,
		pickup_id,
		vehicle_id,
		qr_code,
		cycle_start_time,
		cycle_end_time,
		most_recent_deployment as deployment_number,
		ride_number,
		time_ride_start,
		time_ride_end,
		gross_amount,
		distance,
		start_point,
		end_point
	from 
		(
			select 
				deployment_id,
				pickup_id,
				vehicle_id,
				qr_code,
				cycle_start_time,
				cycle_end_time,
				most_recent_deployment,
				time_ride_start,
				time_ride_end,
				gross_amount,
				distance,
				start_point,
				end_point,
				row_number() over (partition by vehicle_id order by most_recent_deployment asc, time_ride_start desc) as rn,
				row_number() over (partition by vehicle_id, most_recent_deployment order by time_ride_start desc) as ride_number
			from 
				recent_rides
		) as q
	where 
		q.rn <= 5
)
select 
	vehicle_id,
	qr_code,
	json_agg(
		(select x from (select l.deployment_number, l.ride_number, l.gross_amount, l.start_point, l.end_point) as x)
	) as result_to_render
from 
	latest_5_rides as l
group by 
	vehicle_id,
	qr_code;

		