#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from ott.utils import file_utils

from ott.loader.osm.rename.osm_abbr_parser import OsmAbbrParser

import logging
log = logging.getLogger(__file__)


"""
TODO:

2) rename non streets:
<     <tag k="name" v="The Northwest Academy"/>
>     <tag k="name" v="The NW Academy"/>
<     <tag k="name" v="De Paul Treatment Centers"/>
>     <tag k="name" v="De Paul Treatment Ctrs"/>
<     <tag k="name" v="Thai Square"/>
>     <tag k="name" v="Thai Sq"/>

3) don't rename rivers
<     <tag k="name" v="Willamette River"/>
>     <tag k="name" v="Willamette Riv"/>
<     <tag k="destination" v="Columbia River"/>
>     <tag k="destination" v="Columbia Riv"/>


"""

class OsmRename(object):
    """ Utility for getting stats on an osm file 
    """
    attrib = "streets renamed by OpenTransitTools"
    bunchsize = 1000000
    rename_cache = {}

    def __init__(self, osm_infile_path, osm_outfile_path, do_bkup=True):
        """ this class will work to rename streets in OSM, abbreviating common street prefix and suffixes
            (e.g., North == N, Southeast == SE, Street == St, Avenue == Ave, etc...)
            
            :note this assumes that each OSM <tag /> falls completely upon a single line of the file 
            and the parser / renamer will break if targeted tags are spread across multiple lines of the file
            
            
            @todo look at SAX
            https://gist.github.com/veryhappythings/98604
            :todo ... add unit tests
            TODO: fix up hacky parts...
        """
        self.osm_input_path = osm_infile_path
        is_same_input_output = False
        if osm_outfile_path == osm_infile_path:
            self.osm_output_path = osm_outfile_path + "temp"
            is_same_input_output = True
        else:
            self.osm_output_path = osm_outfile_path

        self.abbr_parser = OsmAbbrParser()
        self.process_osm_file()

        if is_same_input_output:
            if do_bkup:
                file_utils.bkup(osm_outfile_path)
            file_utils.mv(self.osm_output_path, osm_outfile_path)

    def process_osm_file(self):
        """ read input xml file line by line.  where we encounter street element tags, look to rename 
            the 'v' attribute (e.g, street name) with 
        """
        bunch = []
        do_rename = False
        is_inside_way = False
        with open(self.osm_input_path, "r") as r, open(self.osm_output_path, "w") as w:
            for line_num, line in enumerate(r):
                # step 1: check to see if this .osm file has already been renamed
                if not do_rename and "<osm " in line:
                    if not self.attrib in line:
                        line = add_xml_attribute_to_osm_tag(line, line_num)
                        do_rename = True

                # step 2: run rename method(s) for this line in the text (xml) file
                if do_rename:
                    if "addr:street" in line:
                        line = self.process_streetname_str(line, line_num, "addr:street")
                    if is_inside_way:
                        if '<tag k="name"' in line or '<tag k="name_' in line:
                            line = self.process_streetname_str(line, line_num, "way:name")
                        elif '<tag k="old_name' in line:
                            line = self.process_streetname_str(line, line_num, "way:old_name")
                        elif '<tag k="bridge:name' in line:
                            line = self.process_streetname_str(line, line_num, "way:bridge:name")
                        elif '<tag k="description' in line:
                            line = self.process_streetname_str(line, line_num, "way:description")
                        elif '<tag k="destination' in line:
                            line = self.process_streetname_str(line, line_num, "way:destination")
                    if '<way ' in line or '<relation ' in line:
                        is_inside_way = True
                    if '</way>' in line or '</relation>' in line:
                        is_inside_way = False

                    # remove ET xml (type html) side effects, so ending tags look trim & proper
                    if line:
                        line = line.replace(" />", "/>").replace("></tag>", "/>")

                # step 3: buffer write the lines of the file to a new file
                bunch.append(line)
                if len(bunch) == self.bunchsize:
                    w.writelines(bunch)
                    bunch = []
            w.writelines(bunch)

    def process_streetname_str(self, line, line_num, type):
        """ parse line of text into XML and look to rename the v attribute in the tag element """
        ret_val = line

        xml = ET.fromstring(line)
        val = xml.get('v')
        if val:
            if len(val) > 0:
                self.rename_xml_value_attirbute(xml, line_num)
                xml_str = ET.tostring(xml, encoding="UTF-8", method="html")
                ret_val = "    {}\n".format(xml_str)
            else:
                log.warn('{} (line {}) xml element {} found an empty street name value'.format(type, line_num, xml.attrib))
        else:
            log.warn('{} (line {}) xml element {} is without a value attribute'.format(type, line_num, xml.attrib))

        return ret_val

    def rename_xml_value_attirbute(self, xml, line_num):
        """ rename the 'v' value attirbute in this xml element tag """
        street_name = xml.attrib['v']
        if street_name in self.rename_cache:
            xml.attrib['v'] = self.rename_cache[street_name]
            if line_num % 111 == 0:
                sys.stdout.write(":")
                sys.stdout.flush()
        else:
            rename = self.abbr_parser.to_str(street_name)
            xml.set('v', rename)
            self.rename_cache[street_name] = rename
            if line_num % 111 == 0:
                sys.stdout.write(".")
                sys.stdout.flush()

    @classmethod
    def rename(cls, osm_infile_path, osm_outfile_path=None, do_bkup=True):
        """ 
        """
        ret_val = None
        if osm_outfile_path is None:
            osm_outfile_path = osm_infile_path
        osm = OsmRename(osm_infile_path, osm_outfile_path)
        return ret_val


def add_xml_attribute_to_osm_tag(line, line_num, attribute_name="generator", attribue_val=OsmRename.attrib, append=True):
    """ a bit hacky <osm> element editing """
    ret_val = line
    try:
        xml = ET.fromstring(line + "</osm>")  # need to fake close elem for ET, since real close is 1000s of lines away
        curr_val = xml.get(attribute_name)
        if append:
            attribue_val = "{}; {}".format(curr_val, attribue_val)
        xml.set(attribute_name, attribue_val)
        ret_val = ET.tostring(xml)
        ret_val = ret_val.replace("</osm>", "").replace("/>", ">")
    except Exception, e:
        log.warn("couldn't add attribute {} to xml element on line number {}", attribute_name, line_num)
        log.warn(e)
    return ret_val


def main():
    """ cmd line processor """
    # cls.rename("ott/loader/osm/cache/or-wa.osm", "ott/loader/osm/cache/or-wa-renamed.osm")
    # cls.rename("ott/loader/osm/cache/portland.osm", "ott/loader/osm/cache/portland-renamed.osm")
    if len(sys.argv) == 2:
        OsmRename(sys.argv[1])
    elif len(sys.argv) > 2:
        OsmRename(sys.argv[1], sys.argv[2])
    else:
        print "what's the path to the osm file?"

