import os

from xml.etree.ElementTree import Element, SubElement, Comment
from xml.etree import ElementTree


class SolrDel(object):
    """ will create an XML document that conforms to SOLR's REST service for deleting items in the index
        <delete>
            <query>type:2</query>
        </delete>

        @see http://lucene.apache.org/solr/quickstart.html#indexing-solr-xml
        @see http://lucene.apache.org/solr/quickstart.html#indexing-json  (@todo maybe move to json)
    """
    type = None
    type_name = None
    file_name = None

    def __init__(self, type, type_name=None, file_name=None):
        self.type = type
        self.type_name = type_name if type_name else self.type
        self.file_name = "{}_del.xml".format(file_name if file_name else self.type_name)

    def to_file(self, path=""):
        doc = ElementTree.Element('delete')
        field = SubElement(doc, 'query')
        field.text = "type_name:{}".format(self.type_name)

        file_path = os.path.join(path, self.file_name)
        doc = ElementTree.tostring(doc, encoding='utf8', method='xml')
        with open(file_path, 'w') as f:
            f.write(doc)
