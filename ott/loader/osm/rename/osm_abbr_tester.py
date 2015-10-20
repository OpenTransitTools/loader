# -*- coding: utf-8 -*-
from pyparsing import *
from osm_abbr_parser import OsmAbbrParser

tests = """\
    3120 De la Cruz Boulevard
    100 South Street
    123 Main
    221B Baker Street
    10 Downing St
    1600 Pennsylvania Ave
    33 1/2 W 42nd St.
    454 N 38 1/2
    21A Deer Run Drive
    256K Memory Lane
    12-1/2 Lincoln
    23N W Loop South
    23 N W Loop South
    25 Main St
    2500 14th St
    12 Bennet Pkwy
    Pearl St
    Bennet Rd and Main St
    19th St
    1500 Deer Creek Lane
    186 Avenue A
    2081 N Webb Rd
    2081 N. Webb Rd
    1515 West 22nd Street
    2029 Stierlin Court
    P.O. Box 33170
    The Landmark @ One Market, Suite 200
    One Market, Suite 200
    One Market
    One Union Square
    One Union Square, Apt 22-C
    """.split("\n")

tests = """\
    De la Cruz Boulevard
    2 SW South St
    2 South St South
    South St South
    33 North South Blvd
    Northwest South Street
    2081 N. Webb Rd
    1515 West 22nd Street
    2029 Stierlin Court
    1 New Orchard Road
    West Wayne Street
    390 Park Avenue
    """.split("\n")

tests = """\
    Southeast Avenue Loop
    Southeast Loop Road
    K Street
    S Street
    C Street
    SW Street
    B Street
    A Street
    K Street North
    North K Street
    South Street
    """.split("\n")


tests = """\
    Southeast 3rd Ave Con't
    Southwest Golf Creek Drive; Southwest Intermark Street
    Charbonneau Drive;Southwest Charbonneau Drive
    Safeway 1627: Truck Service Ramp
    Hubbard Interchange Connection #1
    Wilsonville-Hubbard Highway (Roadway #2)
    """.split("\n")

tests = """\
    Mcloughlin - I205 Ramp Southbound
    Mcloughlin - I205 Ramp South
    South Mcloughlin South
    2 South St South    
    Clackamas-Boring Hwy NO 174
    Southwest Old Highway 47
    Mcloughlin - I205 Ramp Southbound
    Mcloughlin - I205 Ramp South
    South Mcloughlin South
    """.split("\n")

tests = """\
    Cascadia Village Drive - Wallingford Alley
    Southeast 86th Ave-85th Avenue Alley
    Eagle Creek-Sandy Highway NO 172
    I-84 West onramp
    Mcloughlin - I205 Ramp Southbound
    Cascadia Village Drive - Wallingford Alley
    Southeast 86th Ave-85th Avenue Alley
    Eagle Creek-Sandy Highway NO 172
    """.split("\n")




tests = """\
    Main
    Main St
    Bennet Pkwy
    19th St
    NW 19th St
    De la Cruz Boulevard
    North South Street
    Boo Loop
    Avenue A
    Avenue Asd
    South Avenue A
    N Webb Rd
    N. Webb Rd
    West 22nd Street
    19th St SW
    Boo Loop South
    Boo South St Boo St South
    S. South Street
    South Street S.
    South Street
    South
    N.W. South St
    South St S.E.
    Northwest South St S.E.
    Street Street South
    """.split("\n")

tests = """\
    Clackamas-Boring Hwy NO 174
    Southwest Old Highway 47
    Mcloughlin - I205 Ramp Southbound
    Northwest Firelane 3 Road
    Firelane 5 Offshoot
    Parking Lot (Pittock)
    5-4E-18.2 Road
    111H-2 Road
    58 - 120 Spur
    I5 - Carman Ramp Northbound
    B-266 Road
    S-592 Road
    S-592B Road
    W-114 Road
    Fs 2660 Road
    Bureau of Indian Affairs Road 17
    Northeast State Highway 99W
    State Highway 35
    State Highway 224
    Dog River Trail 675
    Southeast Highway 212
    Northwest WA-NA-PA Street
    National Forest Development Road 3511
    Southwest Pacific Highway
    Southeast 3rd Ave Con't
    Veteran's Memorial Freeway
    Saint John's Bridge
    Northwest Saint Andrew's Point
    Tom's Drive
    Southeast Saint Helen's Street
    Southeast Adam's Autobahn
    Coeur d'Alene Drive
    Northeast César E. Chávez Boulevard
    Staint Matthew's Lutheran Church Parking
    Cleveland Avenue Park & Ride
    SW Park Place
    SW Park Ave
    St. Helens Road
    NW St Helens Rd
    """.split("\n")

tests = """\
    Unnamed street
    Southeast 3rd Ave Con't
    Southwest Golf Creek Drive; Southwest Intermark Street
    Charbonneau Drive;Southwest Charbonneau Drive
    Safeway 1627: Truck Service Ramp
    Hubbard Interchange Connection #1
    Wilsonville-Hubbard Highway (Roadway #2)
    Mcloughlin - I205 Ramp Southbound
    Mcloughlin - I205 Ramp South
    South Mcloughlin South
    2 South St South    
    Clackamas-Boring Hwy NO 174
    Southwest Old Highway 47
    Mcloughlin - I205 Ramp Southbound
    Mcloughlin - I205 Ramp South
    South Mcloughlin South
    Clackamas-Boring Hwy NO 174
    Southwest Old Highway 47
    Mcloughlin - I205 Ramp Southbound
    Northwest Firelane 3 Road
    Firelane 5 Offshoot
    Parking Lot (Pittock)
    5-4E-18.2 Road
    111H-2 Road
    58 - 120 Spur
    I5 - Carman Ramp Northbound
    B-266 Road
    S-592 Road
    S-592B Road
    W-114 Road
    Fs 2660 Road
    Bureau of Indian Affairs Road 17
    Northeast State Highway 99W
    State Highway 35
    State Highway 224
    Dog River Trail 675
    Southeast Highway 212
    Northwest WA-NA-PA Street
    National Forest Development Road 3511
    Southwest Pacific Highway
    Southeast 3rd Ave Con't
    Veteran's Memorial Freeway
    Saint John's Bridge
    Northwest Saint Andrew's Point
    Tom's Drive
    Southeast Saint Helen's Street
    Southeast Adam's Autobahn
    Coeur d'Alene Drive
    Northeast César E. Chávez Boulevard
    Staint Matthew's Lutheran Church Parking
    Cleveland Avenue Park & Ride
    Cascadia Village Drive - Wallingford Alley
    Southeast 86th Ave-85th Avenue Alley
    Eagle Creek-Sandy Highway NO 172
    I-84 West onramp
    Mcloughlin - I205 Ramp Southbound
    Cascadia Village Drive - Wallingford Alley
    Southeast 86th Ave-85th Avenue Alley
    Eagle Creek-Sandy Highway NO 172

    """.split("\n")

tests = """\
    Unnamed street
    South West Valley Highway
    North South Shore
    North West XXX Park & Ride
    South South End Court
    South South End Court Alley    
    South Road
    South Shore Road
    South Shore Boulevard
    South Shore Blvd
    East Street
    I5 - Carman Ramp Northbound
    Bureau of Indian Affairs Road 17
    Northeast State Highway 99W
    State Highway 35
    State Highway 224
    National Forest Development Road 3511
    """.split("\n")

xtests = """\
    South Shore Road
    South Shore Boulevard
    South Shore Blvd
    """.split("\n")


sp = OsmAbbrParser()

for name in map(str.strip,tests):
    name = name or ''
    if name:
        try:
            print name
            d = sp.dict(name)
        except ParseException, pe:
            print "EXCEPTION: ", pe
            continue

        print d
        print

'''
        print 'original: ' + name
        print 'name:     ' + addr.name
        print 'type:     ' + sp.find_replace_street_type(addr.type)
        print 'prefix:   ' + sp.find_replace_dir(addr.prefix)
        print 'suffix:   ' + sp.find_replace_dir(addr.suffix)
'''
