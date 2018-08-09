#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pprint
import re

mapping = {"St": "Street",
           "St.": "Street",
           "Ave": "Avenue",
           "Ave.": "Avenue",
           "N.": "North",
           "W.": "West",
           "E": "East",
           "E.": "East",
           "Fdr": "Federal",
           "Streer": "Street",
           "Steet": "Street",
           "S": "South",
           "S.": "South",
           "Avene": "Avenue"
           }


# prints the list of dictionaries line by line
def print_docs(data):
    for doc in data:
        pprint.pprint(doc)


# replace second level tags containing '.' to ':'
def replace_dot(text):
    return text.replace(".",":")


# update name abbreviations
def update_name(name):
    for key in mapping:
        newname = re.sub(r'\b' + key + r'\b\.?', mapping[key], name)
    return newname


# this method helps to project inner tags values in nested dictionary form
def project_innertags(document):
    first_lvl_doc = {}
    second_lvl_doc = {}
    for tag in document:
        if tag in ('name', 'name:en', 'addr:name'):
            document[tag] = update_name(document[tag])
        if ':' in tag:
            level_keys = tag.split(':')
            second_lvl_doc[level_keys[1]] = document[tag]
            first_lvl_doc[level_keys[0]] = second_lvl_doc
        else:
            first_lvl_doc[tag] = document[tag]
    return first_lvl_doc


# process only containing inner tags
def process_innertags(data):
    elements = []
    for el in data:
        if 'inner_tags' in el:
            projection = project_innertags(el['inner_tags'])
            del el['inner_tags']
            el.update(projection)
            elements.append(el)
    return elements
