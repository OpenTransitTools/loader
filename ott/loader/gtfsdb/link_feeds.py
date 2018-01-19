"""
SHARED STOPS TABLE
shared_stop_id (seq), stop_id, agency_id, agency_stop_id, agency_db_schema, distance

ROUTE INTERSECTS TABLE
route_id, agency_id, agency_route_id, agency_db_schema, closest_shared_stop_id
(is this table really necessary? )

Between 2 different GTFS feeds (e.g., TriMet and SMART, or TriMet and C-Tran, etc...) there are a handful of shared
stops, but each are defined in their respective Agency GTFS feed.  Further, we can link show which transit lines touch
each other within a given distance between stops, etc...

What:
 - pre-calculate what we think are shared stops between multiple gtfs feeds.
 - pre-calculate route intersections

Borrow linking ideas from this:
https://github.com/laidig/transloc-gtfs-rectifier/blob/master/recitfy_gtfs.py#L38

"""

class LinkFeeds(object):
    """
    """
    def __init__(self):
        pass
