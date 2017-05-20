try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from ott.utils import file_utils

import logging
log = logging.getLogger(__file__)



class OsmRename(object):
    """ Utility for getting stats on an osm file 
    """
    attrib = "renamed by OTT"
    bunchsize = 1000000
    rename_cache = {}

    def __init__(self, osm_infile_path, osm_outfile_path):
        """ this class will work to rename streets in OSM, abbreviating common street prefix and suffixes
            (e.g., North == N, Southeast == SE, Street == St, Avenue == Ave, etc...)
            
            :note this assumes that each OSM <tag /> falls completely upon a single line of the file 
            and the parser / renamer will break if targeted tags are spread across multiple lines of the file
        """
        self.osm_input_path = osm_infile_path
        is_same_input_output = False
        if osm_outfile_path == osm_infile_path:
            self.osm_output_path = osm_outfile_path + "temp"
            is_same_input_output = True
        else:
            self.osm_output_path = osm_outfile_path

        self.process_osm_file()

        if is_same_input_output:
            file_utils.backup(osm_outfile_path)
            file_utils.mv(self.osm_output_path, osm_outfile_path)

    def process_osm_file(self):
        """ read input xml file line by line.  where we encounter street element tags, look to rename 
            the 'v' attribute (e.g, street name) with 
        """
        bunch = []
        do_rename = False
        with open(self.osm_input_path, "r") as r, open(self.osm_output_path, "w") as w:
            for line_num, line in enumerate(r):
                # step 1: check to see if this .osm file has already been renamed
                if not do_rename and "<osm " in line:
                    if not self.attrib in line:
                        line = add_xml_attribute_to_tag(line, line_num)
                        do_rename = True

                # step 2: run rename method(s) for this line in the text (xml) file
                if do_rename:
                    if "addr:street" in line:
                        line = self.process_addrstreet_line(line, line_num)

                # step 3: buffer write the lines of the file to a new file
                bunch.append(line)
                if len(bunch) == self.bunchsize:
                    w.writelines(bunch)
                    bunch = []
            w.writelines(bunch)

    def process_addrstreet_line(self, line, line_num):
        """ parse line of text into XML and look to rename the v attribute in the tag element """
        ret_val = line

        xml = ET.fromstring(line)
        val = xml.get('v')
        if val:
            if len(val) > 0:
                self.rename_xml_value_attirbute(xml)
                ret_val = ET.tostring(xml)
            else:
                log.warn('addr:street (line {}) xml element {} found an empty street name value'.format(line_num, xml.attrib))
        else:
            log.warn('addr:street (line {}) xml element {} is without a value attribute'.format(line_num, xml.attrib))

        return ret_val

    def rename_xml_value_attirbute(self, xml):
        """ rename the 'v' value attirbute in this xml element tag """
        street_name = xml.attrib['v']
        if street_name in self.rename_cache:
            xml.attrib['v'] = self.rename_cache[street_name]
        else:
            rename = street_name + "XXX"
            xml.setAttribute('v', rename)
            self.rename_cache[street_name] = rename

    @classmethod
    def rename(cls, osm_infile_path, osm_outfile_path):
        """ 
        """
        #import pdb; pdb.set_trace()
        ret_val = None

        # step 1: validate stats file path
        osm = OsmRename(osm_infile_path, osm_outfile_path)

        # step 4: return the stats as a string
        return ret_val

    @classmethod
    def mock(cls):
        """ assumes portland.osm exists """
        #cls.rename("ott/loader/osm/cache/or-wa.osm", "ott/loader/osm/cache/or-wa-renamed.osm")
        cls.rename("ott/loader/osm/cache/portland.osm", "ott/loader/osm/cache/portland-renamed.osm")



def add_xml_attribute_to_tag(line, line_num, attribute_name="generator", attribue_val=OsmRename.attrib, append=True):
    ret_val = line
    try:
        xml = ET.fromstring(line)
        curr_val = xml.get(attribute_name)
        if append:
            attribue_val = "{}; {}".format(curr_val, attribue_val)
        xml.set(attribute_name, attribue_val)
        ret_val = ET.tostring(xml)
    except Exception, e:
        log.warn("couldn't add attribute {} to xml element on line number {}", attribute_name, line_num)
        log.warn(e)
    return ret_val
