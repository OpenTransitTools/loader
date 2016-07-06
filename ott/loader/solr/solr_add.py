import datetime

from xml.etree.ElementTree import Element, SubElement, Comment
from xml.etree import ElementTree

class SolrAdd(object):
    """ will create an XML document that conforms to SOLR's REST service for adding items to the index
        @todo investigate using SolrPy (not sure why I didn't think of this before)
        @see
    """
    rec = None
    doc = None

    def __init__(self, boost='1.0', comment=''):
        self.header(boost, comment)

    def header(self, boost, comment):
        self.rec = ElementTree.Element('add')
        cmt_el = ElementTree.Comment(' Generated on {} {} '.format(datetime.date.today(), comment))
        self.rec.append(cmt_el)
        self.doc = SubElement(self.rec, 'doc', attrib={'boost' : boost})

    def add_field(self, name, value):
        field = SubElement(self.doc, 'field', attrib={'name':name})
        field.text = value

    def document_to_string(self):
        return ElementTree.tostring(self.rec, encoding='utf8', method='xml')
