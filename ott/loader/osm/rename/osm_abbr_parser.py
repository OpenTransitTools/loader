# -*- coding: utf-8 -*-
# DON'T DELETE ^^^ THIS ^^^ LINE ABOVE (needed for crap down below)

import os
import inspect
import csv

from pyparsing import *


class OsmAbbrParser(object):
    """
    Convert long OSM types and directions to their proper abbreviated forms
    """
    this_module_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))


    def __init__(self):
        """
        constructor builds the pyparsing parser
        """

        # step 1: load in .csv files used for parsing, find/replace and string fixups
        self.street_types_kw, self.street_types = self.load_replace_csv('street_types.csv')
        self.dir_types_kw,    self.dir_types    = self.load_replace_csv('dir_types.csv')
        self.str_replace_kw,  self.str_replace  = self.load_replace_csv('string_replace.csv')
        self.str_ignore_kw,   self.str_ignore   = self.load_replace_csv('string_ignore_replace.csv')
        self.str_ignore_kw = self.str_ignore_kw.lower()

        # step 2a: build the keyword list for street types from our .csv files
        st = map(CaselessKeyword, self.street_types_kw.split())
        type_ = Combine(MatchFirst(st) + Optional(".").suppress())

        # step 2b: build the keyword list for direction types from our .csv files
        dt = map(CaselessKeyword, self.dir_types_kw.split())
        prefix = Combine(StringStart() + MatchFirst(dt) + Optional(" ") + Optional(".").suppress())
        suffix = Combine(OneOrMore(MatchFirst(dt) + Optional(".").suppress()) + StringEnd())

        name_chars = nums + alphas + "-" + "." + "," + "á" + "é" + "." + "'" + '"' + "&" + ";" + ":" + "#" + "@" + "(" + ")"
        name_string = Word(name_chars) 
        street_name = (
                       Combine( 
                            OneOrMore(
                                 ~prefix + ~type_ + ~suffix + name_string
                                 |
                                 ~type_ + ~suffix + name_string
                                 |
                                 type_  + FollowedBy(name_string) + FollowedBy(~suffix)
                                 ), joinString=" ", adjacent=False)
                     ).setName("streetName")

        # basic street address grammer
        nm = street_name.setResultsName("name")
        tp = type_.setResultsName("type")
        pre = prefix.setResultsName("prefix") 
        nm_type = nm + tp
        pre_nm_type = pre + nm + tp
        pre_nm = pre + nm
        suf = suffix.setResultsName("suffix") 
        suf_nm_type = nm + tp + suf
        suf_nm = nm + suf
        self.streetAddress = ( 
                          suf_nm_type
                          | suf_nm
                          | pre_nm_type
                          | pre_nm
                          | nm_type
                          | nm
                        )

    def parse(self, s):
        """
        Returns parsed address as dictionary
        run the input string through the street parser
        """
        ret_val = {
           'type':   '',
           'suffix': '',
           'prefix': '',
           'name':   '',
        }
        r = ret_val
        # test whether this string is in our ignore list (e.g., South Shore Blvd) before sending to the parser  
        if s.lower() in self.str_ignore_kw:
            d = self.csv_ignore_replace(self.str_ignore, s)
            r['name'] = d['replace']
            r['type'] = d['type']
            r['prefix'] = d['prefix']
            r['suffix'] = d['suffix']
        else:
           p = self.streetAddress.parseString(s)
           r['type'] = self.find_replace(self.street_types, p.type)
           r['suffix'] = self.find_replace(self.dir_types,    p.suffix)
           r['prefix'] = self.find_replace(self.dir_types,    p.prefix)
           r['name'] = p.name

        return ret_val

    def dict(self, orig):
        """
        Returns a parsed and string replaced dict

        dict format is {
                         original:'East North South Street Westbound',
                         name:'North South',
                         type:'St', prefix:'E', suffix:'WB',
                         label_text: 'E North South St WB',
                         label: TRUE (or FALSE)
                       }
        """
        s = self.sub_str_replace(self.str_replace, orig)
        ret_val = r = self.parse(s)
        pretty = ""
        pretty = self.pstr(r['prefix'], pretty) + self.pstr(r['name'], pretty) + self.pstr(r['type'], pretty) + self.pstr(r['suffix'], pretty)
        ret_val['label_text'] = pretty.strip()
        ret_val['label'] = self.do_label(r['name'], r['type'])
        return ret_val

    def to_str(self, orig):
        ret_val = orig
        try:
            f = self.dict(orig)
            if f and len(f['label_text']) > 0:
                ret_val = f['label_text']
        except:
            pass
        return ret_val

    def do_label(self, s, t):
        ret_val = True
        s = s.lower()
        if s == "unnamed" or t == "Aly":
            ret_val=False
        return ret_val

    def pstr(self, s, r):
        """
        return a pretty string by checking string len, and return the string, with optional trailing space...
        """
        if r is None and len(s) <= 0:
            r = ""
        if s is not None and len(s) > 0:
            if len(s) > 0:
                r += " "
            r += s
        return r

    def dict_find(self, dict, value, col='str'):
        """
        """
        ret_val = False
        l = dict[col].lower()
        v = value.lower()
        if v.find(l) >= 0:
            ret_val = True
        return ret_val

    def csv_ignore_replace(self, csv_list, value):
        """
        """
        ret_val = None
        # search the 'str' column for a csv entry...
        for i, dic in enumerate(csv_list):
            if self.dict_find(dic, value):
                ret_val = dic
                break
        if ret_val is None:
            # if not found in the 'str' column, search the 'replace' column for a csv entry...
            for i, dic in enumerate(csv_list):
                if self.dict_find(dic, value, 'replace'):
                    ret_val = dic
                    break
        return ret_val

    def sub_str_replace(self, lst, value, justOnce=False):
        """ find a value in a list of dicts, key identifies what attribute of the dict to look at
        """
        ret_val = value
        for i, dic in enumerate(lst):
            if self.dict_find(dic, value):
                ret_val = ret_val.replace(dic['str'], dic['replace'], 1)
                if justOnce:
                    break
        return ret_val

    def find_list_pos(self, lst, key, value):
        """ find position of matching dict  in a list of dicts, key identifies what attribute of the dict to compare to the value
        """
        ret_val = -1
        for i, dic in enumerate(lst):
            if dic[key].strip().lower() == value.strip().lower():
                ret_val = i
                break
        return ret_val

    def find_replace(self, lst, value):
        """ returns a matching replacement string from a list of dicts with the form [{str:"XTC", replace:"Atom Ant"}, ...]
            returns passed in 'value' param if the string is not in the dict list

            call find on the list, and when a match is found, the 'replace' attribute will be returned
        """
        i = self.find_list_pos(lst, 'str', value)
        if i == -1:
           i = self.find_list_pos(lst, 'replace', value)
        if i == -1:
           return value
        d = lst[i]
        return d['replace']

    def load_replace_csv(self, fn):
        """ returns a large string with the 'str' and 'replace' attributes concat'd together (used as keywords in pyparsing)
            returns a list of dicts of the form [{str:"XTC", replace:"Atom Ant"}, ...]

            from a .csv file, builds mappings that provide both keywords for the parser and a list of text replacement dicts
        """
        # street types -- used for both parser and replacement
        csv_path = os.path.join(self.this_module_dir, fn)
        f = open(csv_path, 'r')
        reader = csv.DictReader(f)
        strings = ""
        l = []
        for row in reader:
           strings += row['str'] + " " + row['replace'] + " "
           l.append(row)

        return strings, l
