# Filename: xml_csv_validation_routines.py
# Python 3.7

import csv
from collections import defaultdict
import os
import sys
import re
import pprint

# Check the number of rows in csv files

csv_counts = defaultdict(int)

def csv_row_count():
    """Prints the number of rows in the CSV files and returns None."""

    if not os.path.exists("nodes_tags.csv"):
        print ("Cannot find CSV files...")
        sys.exit()

    print ('\nCSV FILE RECORD COUNTS\n')

    with open('nodes.csv', 'r') as csv_file:
        reader = csv.reader(csv_file)   # comma is default delimiter
        csv_counts['nodes_row_count'] = sum(1 for row in reader)

    print ('Node number of rows: {:,}'.format(csv_counts['nodes_row_count'] - 1))  # Subtract header row
    csv_file.close()

    with open('nodes_tags.csv', 'r') as csv_file:
        reader = csv.reader(csv_file)   # comma is default delimiter
        csv_counts['nodes_tags_row_count'] = sum(1 for row in reader)

    print ('Node tags number of rows: {:,}'.format(csv_counts['nodes_tags_row_count'] - 1))  # Subtract header row
    csv_file.close()

    with open('ways.csv', 'r') as csv_file:
        reader = csv.reader(csv_file)   # comma is default delimiter
        csv_counts['ways_row_count'] = sum(1 for row in reader)

    print ('\nWay number of rows: {:,}'.format(csv_counts['ways_row_count'] - 1))  # Subtract header row
    csv_file.close()

    with open('ways_tags.csv', 'r') as csv_file:
        reader = csv.reader(csv_file)   # comma is default delimiter
        csv_counts['ways_tags_row_count'] = sum(1 for row in reader)

    print ('Way tags number of rows: {:,}'.format(csv_counts['ways_tags_row_count'] - 1))  # Subtract header row
    csv_file.close()

    with open('ways_nodes.csv', 'r') as csv_file:
        reader = csv.reader(csv_file)   # comma is default delimiter
        csv_counts['ways_nodes_row_count'] = sum(1 for row in reader)

    print ('Way Node number of rows: {:,}'.format(csv_counts['ways_nodes_row_count'] - 1))  # Subtract header row
    csv_file.close()
    return


# Count all the tags in the XML file
# Reconcile check for number of records in csv files

map_file = 'UpperWestSideTest.osm'

tags = defaultdict(int)
children = defaultdict(int)
problem_counts = defaultdict(int)

valid_keys = [  "addr:housenumber",
                "amenity",
                "name",
                "cuisine",
                "shop",
                "building",
                "addr:street",
                "addr:state",
                "addr:city",
                "addr:postcode",
                "phone",
                "email",
                "website",
                "url",
                "tiger:reviewed",
                "inscription_1",
                "inscription_2",
                "inscription_date",
                "nrhp:inscription_date"]

correct_chars_re = re.compile(r"^[a-zA-Z:\-_1-9]+$")

def initialize():
    """Clears the dictionaries and returns a boolean."""
    try:
        tags.clear()
        children.clear()
        problem_counts.clear()
        return True
    except:
        return None

def check_id(id):
    """Checks the ID is valid and returns it or None if it is invalid.
    
    Arguments:
    id -- the ID number attribute of the element tags <node> or <way>
    """
    id = id.strip()
    
    if id and id.isdigit():   # id must only be a number
        return id
    else:
        return None

def separator(dict):
    """Formats values in a dictionary with the thousands separator and returns the dictionary.
    
    Arguments:
    dict -- the dictionary to be formatted
    """
    for k,v in dict.items():
        v = "{:,}".format(v)
        dict[k] = str(v)
        
    return dict

import xml.etree.cElementTree as ET

def element_tree(osm_file):
    """Parse XML file data and yield an element tree.
       
    Iteratively step through each top level XML element and read in sections of the XML file 
    as a tree of the element
    
    Arguments:
    osm_file -- the Open Street Map XML file to process
    """
    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)      # root saves a reference to the iterator (block of XML) currently in process
 
    for event, element in context:    # the result is an iterable that returns a stream of (event, element) tuples 
        if event == 'end':            # end returns the fully populated element (including children)
            yield element        # yield returns a generator
            root.clear()
    
    del context
    return

def count_xml_tags(filename):
    """Counts all the tags in the XML file and returns None.
    
    Reconcile check for the number of records in the CSV files
    
    Arguments:
    filename -- the Open Street Map XML file to process
    """
    for element in element_tree(filename):
        bad_id = False
        tags[element.tag] += 1
        
        if element.tag == 'node':
            check = check_id(element.attrib['id'])
            if not check:
                print ('Node ID is Null or not a number: ', element.attrib['id'])
                problem_counts['node id bad'] += 1
                bad_id = True     # No continue here because counting ALL tags
                
        if element.tag == 'way':
            check = check_id(element.attrib['id'])
            if not check:
                print ('Way ID is Null or not a number: ', element.attrib['id'])
                problem_counts['way id bad'] += 1
                bad_id = True     # No continue here because counting ALL tags
        
        for child in element:
            if child.tag == 'nd':     # Check the 'nd' way node element for ID
                if bad_id:
                    problem_counts['nd bad'] += 1
                    print ('Way node ID is bad: ', element.attrib['id'])
                else:
                    check = check_id(child.attrib['ref'])    # Check the 'nd' way node element for reference ID
                    if not check:
                        problem_counts['nd bad'] += 1
                        print ('Way node reference is bad: ', child.attrib['ref'])
                
            if child.tag == 'tag' and (child.attrib['k'] in valid_keys) and bad_id:    # Valid keys with bad ID
                if element.tag == 'node':
                    print ('   ', element.tag.capitalize(), ':  k = ', child.attrib['k'], '  id = ', element.attrib['id'], '   Problem: Corrupt ID')
                    problem_counts['node tag bad'] += 1
                if element.tag == 'way':
                    print ('   ', element.tag.capitalize(), ':  k = ', child.attrib['k'], '  v = ', child.attrib['v'],'  id = ', element.attrib['id'], '   Problem: Corrupt ID')
                    problem_counts['way tag bad'] += 1
                        
            if child.tag == 'tag' and (element.tag in ['node', 'way']) and not bad_id:  #Note: Bad keys with good ID
                m = not correct_chars_re.search(child.attrib['k'])         # Check for corrupt keys
                if m and not ('cityracks' in child.attrib['k']):
                    if element.tag == 'node':
                        print ('   ', element.tag.capitalize(), ':  k = ', child.attrib['k'], '  id = ', element.attrib['id'], '   Problem: Corrupt key')
                        problem_counts['node key bad'] += 1
                    if element.tag == 'way':
                        print ('   ', element.tag.capitalize(), ':  k = ', child.attrib['k'], '  id = ', element.attrib['id'], '   Problem: Corrupt key')
                        problem_counts['way key bad'] += 1
            
            try:
                child_key = child.attrib['k']
            except:
                child_key = None
                continue
            
            if (element.tag in ['node', 'way']) and (child_key in valid_keys):
                children[element.tag + ' ' + child_key] += 1
                children['Total child tags'] += 1
                if element.tag == 'node':
                    children['Total node tags'] += 1
                else:
                    children['Total way tags'] += 1
    
    return

def count_all_tags():
    """Calls the count routines, prints a report, and returns None."""
    response = initialize()
    if not response:
        print ("Cannot perform initialization...")
        print ("...program execution terminated")
        return None
    
    print ('\n---------------------')
    print ('XML FILE TAG PROBLEMS\n')
    count_xml_tags(map_file)
    
    total = sum(tags.values())
    
    separator(tags)
    separator(children)
    
    print ("\n-------------------")
    print ("XML FILE TAG COUNTS\n")
    print ("• Nodes: ", tags['node'])
    print ("• Ways: ", tags['way'])
    print ("• Ways Nodes: ", tags['nd'], "\n")
    print ("• Nodes tags: ", children['Total node tags'])
    print ("• Ways tags: ", children['Total way tags'], "\n")
    
    print ("Total sum of XML tags processed: {:,}".format(total) )
    
    print ("\n----------------")
    print ("XML PROBLEM TAGS\n")
    print ("Node ID problem: ", problem_counts['node id bad'])
    print ("Way ID problem: ", problem_counts['way id bad'])
    print ("Way Node problem: ", problem_counts['nd bad'])
    print ("Node tag problem: ", problem_counts['node tag bad'])
    print ("Way tag problem: ", problem_counts['way tag bad'])
    
    print ("\nNode tag key problem: ", problem_counts['node key bad'])
    print ("Way tag key problem: ", problem_counts['way key bad'])
    
    print ("\n------------")
    print ("ELEMENT TAGS\n")
    pprint.pprint(tags)
    print ("\n----------")
    print ("CHILD TAGS\n")
    pprint.pprint(children)
    return


# Print a table of the reconciled CSV and XML count differences

from prettytable import PrettyTable

def make_table():
    """Prints a table of the reconciled CSV and XML count differences and returns None."""
    pt = PrettyTable()

    pt.field_names = ["             ", " XML Tag Count ", " Eliminated XML Tags ", " CSV Record Count ", 
                      " Difference is Tags Eliminated "]
    pt.add_row([" ", " ", " ", " ", " "])

    pt.add_row([" <node> <tag> ", children['Total node tags'], problem_counts['node tag bad'], "{:,}".format(csv_counts['nodes_tags_row_count'] - 1), 
                   (int(children['Total node tags'].replace(',', '')) - (csv_counts['nodes_tags_row_count'] - 1) - problem_counts['node tag bad'])])

    pt.add_row([" ", " ", " ", " ", " "])

    pt.add_row([" <way> <tag> ", children['Total way tags'], problem_counts['way tag bad'], "{:,}".format(csv_counts['ways_tags_row_count'] - 1), 
                   (int(children['Total way tags'].replace(',', '')) - (csv_counts['ways_tags_row_count'] - 1) - problem_counts['way tag bad'])])

    pt.add_row([" ", " ", " ", " ", " "])

    pt.add_row([" <node> ", tags['node'], problem_counts['node id bad'], "{:,}".format(csv_counts['nodes_row_count'] - 1), 
                   (int(tags['node'].replace(',', '')) - (csv_counts['nodes_row_count'] - 1) - problem_counts['node id bad'])])

    pt.add_row([" ", " ", " ", " ", " "])

    pt.add_row([" <way> ", tags['way'], problem_counts['way id bad'], "{:,}".format(csv_counts['ways_row_count'] - 1), 
                   (int(tags['way'].replace(',', '')) - (csv_counts['ways_row_count'] - 1) - problem_counts['way id bad'])])

    pt.add_row([" ", " ", " ", " ", " "])

    pt.add_row([" <way node> ", tags['nd'], problem_counts['nd bad'], "{:,}".format(csv_counts['ways_nodes_row_count'] - 1), 
                   (int(tags['nd'].replace(',', '')) - (csv_counts['ways_nodes_row_count'] - 1) - problem_counts['nd bad'])])

    print ('\n    ---------------------------------')
    print ("    TABLE OF RECORD COUNT DIFFERENCES\n")
    print(pt)
    return


def create_validation_table():
    """Reconciles the tag count differences between the CSV and XML files, prints a table, and returns None."""
    response = initialize()
    if not response:
        print ("Cannot perform initialization...")
        print ("...program execution terminated")
        return None

    if not os.path.exists("nodes_tags.csv"):
        print ("Cannot find CSV files...")
        sys.exit()

    csv_row_count()
    count_all_tags()
    make_table()
    return

#========================#
#         Runner         #
#========================#

if __name__ == '__main__':
    create_validation_table()
