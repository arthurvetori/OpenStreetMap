#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dbadapter import *
from clean import *
import pprint
from collections import defaultdict
import re
import xml.etree.cElementTree as ET
import codecs
import json


map_file = 'map.xml'
json_file = "{0}.json".format(map_file)

street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

element_types = ['way', 'node', 'relation']

expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road",
            "Trail", "Parkway", "Commons"]

# count each upper level tag type
def count_tags(filename):
        tags = {}
        doc = ET.parse(filename)
        for elm in doc.iter():
            if elm.tag in tags:
                tags[elm.tag] += 1
            else:
                tags[elm.tag] = 1
        return tags

# list all possibilities for tags
def map_tag_keys(filename):
    keys = set()
    for _, element in ET.iterparse(filename):
        if element.tag in ('node', 'way'):
            for c in element.iter():
                if c.tag == "tag":
                    keys.add(c.attrib['k'])
    return keys


# get the user from element
def get_user(element):
    return element.attrib.get('user')


# get all unique users from the osm file
def process_users(filename):
    users = set()
    for _, element in ET.iterparse(filename):
        if element.tag in element_types:
            users.add(get_user(element))

    return users

# verify if streetname is in expected street types defined early
def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)

# verify if attribute is street name
def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")

# audit the file, generating a set over a possible street names
def audit(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    osm_file.close()
    return street_types

# shape element and prepare it to insert in json format
def shape_element(element):
    node = {}
    lat = 0.0
    lon = 0.0
    if element.tag == "node" or element.tag == "way" :
        node = {
            "id" : element.attrib["id"],
            "type" : element.tag,
            "created" : {
                "version" : element.attrib["version"],
                "changeset" : element.attrib["changeset"],
                "timestamp" : element.attrib["timestamp"],
                "user" : element.attrib["user"],
                "uid": element.attrib["uid"]
            },
        }
        if element.attrib.get("lat") is not None:
            lat = float(element.attrib["lat"])
            lon = float(element.attrib["lon"])
            node["pos"] = [lat, lon]
        refs = []
        inner_tags = {}
        for child in element.iter():
            if child.tag == "tag":
                inner_tags[replace_dot(child.attrib['k'])] = child.attrib['v']
                if inner_tags:
                    node["inner_tags"] = inner_tags
            if child.tag == "nd":
                refs.append(child.attrib["ref"])
                if refs:
                    node["node_refs"] = refs

        return node
    else:
        return None

# process the map file, generating a list of documents in JSON format
def process_map(file_in):
    data = []
    for _, element in ET.iterparse(file_in):
        el = shape_element(element)
        if el:
            data.append(el)

    return data


# write the data into json format
def dump_data(data, file_out = None):
    if file_out is None:
        file_out = json_file
    with codecs.open(file_out, "w") as fo:
        for element in data:
            if element is not None:
                json.dump(element, fo)



def run():

    # get more info about tags in the map
    tags_num = count_tags(map_file)
    tags_type = map_tag_keys(map_file)

    # audit the file
    audit_street_set = audit(map_file)

    # process all data
    all_data = process_map(map_file)
    # process only the data that cointains inner level tags like ' k '
    detailed_data = process_innertags(all_data)

    # dump data to file
    dump_data(all_data)
    dump_data(detailed_data, 'map_detailed.xml.json')

    # insert into mongo database with collections name ' all_data ' and ' detailed_data ' on database ' DAND '
    db_insert(all_data, 'all_data')
    db_insert(detailed_data, 'detailed_data')


if __name__ == '__main__':
    # run the data processing
    run()
