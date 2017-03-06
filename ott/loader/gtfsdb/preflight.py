"""
> We need a way to hold off trip planning on preliminary exports.  Can we set an end date for the GTFS export to exclude incomplete schedules?

TODO: add checks to GTFS … make sure each service date has multiple service keys, make sure each service date has many multiple trips…



From: Kellermann, John
Sent: Wednesday, August 17, 2016 1:09 PM
To: Gilligan, Mike; Fisher, Rex; Gillespie, Bryan
Cc: Purcell, Frank; Boyd, Joshua
Subject: RE: No MAX schedules on September 4th & 5th

See:
H:\Export\ToTrans_14\Production

Looks like Rex did not include the holiday in the initial export for timetables (July 7), perhaps because they weren’t ready.
2016_09_04_sched_16TU.txt

He set up a separate export for the holiday, perhaps to debug it.
2016_09_04_sched_16TU-holiday.txt

We need a way to hold off trip planning on preliminary exports.  Can we set an end date for the GTFS export to exclude incomplete schedules?

From: Gilligan, Mike
Sent: Wednesday, August 17, 2016 12:59 PM
To: Fisher, Rex; Gillespie, Bryan; Kellermann, John
Cc: Purcell, Frank; Boyd, Joshua
Subject: RE: No MAX schedules on September 4th & 5th

Actually, we don’t have any active trips for bus or rail on September 5th because there are no service_key = ‘X’ trips defined.

From: Gilligan, Mike
Sent: Wednesday, August 17, 2016 12:54 PM
To: Fisher, Rex; Gillespie, Bryan; Kellermann, John
Cc: Purcell, Frank; Boyd, Joshua
Subject: No MAX schedules on September 4th & 5th
Importance: High

Hi all-

Frank sent me a message yesterday and I just investigated it. It appears we do not have any MAX trips active on September 4th or 5th, according the export from Hastus.

Can anyone explain to me why or how I might be able to resolve it? Adding some calendar entries?

Thanks,
-Mike

"""

class Preflight(object):
    """ check the gtfsdb for proper tables and sizes
    """
    def __init__(self):
        pass
