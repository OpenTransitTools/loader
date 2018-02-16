"""
    Credit goes to https://stackoverflow.com/users/684592/kotaro
    https://stackoverflow.com/questions/14716497/how-can-i-find-a-list-of-street-intersections-from-openstreetmap-data?rq=1
"""

from ott.utils import file_utils

try:
    from xml.etree import cElementTree as ET
except ImportError, e:
    from xml.etree import ElementTree as ET


def extract_intersections(osm):
    """
    This method reads the passed osm file (xml) and finds intersections (nodes that are shared by two or more roads)
    :param osm: An osm file or a string from get_osm()
    """
    ret_val = []

    # step 1: parse either XML string or file
    if '<' in osm and '>' in osm:
        tree = ET.fromstring(osm)
        children = tree.getchildren()
    else:
        tree = ET.parse(osm)
        root = tree.getroot()
        children = root.getchildren()

    counter = {}
    for child in children:
        if child.tag == 'way':
            is_road = False

            # TODO: make road types configurable
            road_types = ('primary', 'secondary', 'residential', 'tertiary', 'service')
            for item in child:
                if item.tag == 'tag' and item.attrib['k'] == 'highway' and item.attrib['v'] in road_types:
                    is_road = True
                    break

            if is_road:
                for item in child:
                    if item.tag == 'nd':
                        nd_ref = item.attrib['ref']
                        if nd_ref not in counter:
                            counter[nd_ref] = 0
                        counter[nd_ref] += 1

    # Find nodes that are shared with more than one way, which might correspond to intersections
    intersections = filter(lambda x: counter[x] > 1, counter)

    for child in children:
        if child.tag == 'node' and child.attrib['id'] in intersections:
            coordinate = child.attrib['lat'] + ',' + child.attrib['lon']
            ret_val.append(coordinate)

    return ret_val


def main():
    # import pdb; pdb.set_trace()
    dir = file_utils.get_file_dir(__file__)
    file = file_utils.path_join(dir, './tests/portland.osm')
    intersections = extract_intersections(file)
    for entry in intersections:
        print entry


if __name__ == '__main__':
    main()
