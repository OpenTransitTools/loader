psql -d ott -c "update trimet.current_stops set route_type=111, route_mode='SC' where route_short_names like '%Streetcar%'"
