create or replace function fn_calculate_distance(lat1 float, lon1 float, lat2 float, lon2 float, units varchar)
returns float as $dist$
    declare
        dist float = 0;
        radlat1 float;
        radlat2 float;
        theta float;
        radtheta float;
    begin
        if lat1 = lat2 or lon1 = lon2
            then return dist;
        else
            radlat1 = pi() * lat1 / 180;
            radlat2 = pi() * lat2 / 180;
            theta = lon1 - lon2;
            radtheta = pi() * theta / 180;
            dist = sin(radlat1) * sin(radlat2) + cos(radlat1) * cos(radlat2) * cos(radtheta);

            if dist > 1 then dist = 1; end if;

            dist = acos(dist);
            dist = dist * 180 / pi();
            dist = dist * 60 * 1.1515;

            if units = 'K' then dist = dist * 1.609344; end if;
            if units = 'N' then dist = dist * 0.8684; end if;

            return dist;
        end if;
    end;
$dist$ language plpgsql;