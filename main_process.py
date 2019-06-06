# Filename: main_process.py
# Python 3.7
# Purpose: Validate and save the element dictionary to csv files

# Send each element in the XML file to the "build_dictionary_element" function (in file "element_to_dictionary.py")
# Validate the returned element dictionary against the schema and save it to csv files where the csv data can 
#   be imported to an SQL database for data analysis.

# The element is examined and for each child in the element, the child 'value' is sent to 
#   the "fix_it" function (in file "fix_it.py") for correcting.
# A Python dictionary is constructed and returned back to the "process_xml_elements" function
#   (in file "main_process.py") for saving into the csv file.

import csv
import codecs
import pprint
import re
import xml.etree.cElementTree as ET
import cerberus
import sys

#==========================#
#     Import .py files     #
#==========================#

import db_schema
import element_to_dictionary
import fix_it

#===============================#
#     Initialize file names     #
#===============================#

OSM_PATH = "UpperWestSideTest.osm"    # Test file size is 10.1MB
SCHEMA = db_schema.schema

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

#=========================================#
#     Construct and initialize lists      #
#=========================================#

# Be sure the field order in the csv matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']

# =============================================================== #
#               Main Process Helper Functions                     #
# =============================================================== #

def get_element_tree(osm_file, tags=('node', 'way')):
    """Parse XML file data and yield an element tree.
       
    Iteratively step through each top level XML element <node> or <way> 
    and read in sections of the XML file as a tree of the element
    
    Arguments:
    osm_file -- the Open Street Map XML file to process
    tags -- list of XML parent tags to process
    """
    context = ET.iterparse(osm_file, events=('start', 'end'))
        # iterparse returns a stream of events between start and end.
        # Returns an iterator providing (event, element) pairs
        # parses an XML section into an element tree incrementally
    _, root = next(context)
        # root saves a reference to the iterator (block of XML) currently in process
        # next() returns the next item in an iterator. Do not use context.next() in Python 3
        # _ is a dummy variable for event. We are only interested in the root reference  
    
    for event, element in context:    # the result is an iterable that returns a stream of (event, element) tuples 
        if event == 'end':            # end returns the fully populated element (including children)
            fix_it.counts['element count'] += 1
            if element.tag in tags:
                yield element        # yield returns a generator
                root.clear()         # remove the XML section from memory
            else:
                fix_it.counts['not a node or way count'] += 1
    
    del context
    return

#  Raise Validation Error if dictionary does not match schema
def validate_dictionary(dict, validator, schema=SCHEMA):
    """Runs the Cerberus data validation library to validate the dictionary against the schema.
    
    Raises an exception for a validation error, or returns None if dictionary is valid
    
    Arguments:
    dict -- the element tree dictionary for the current element tree in the XML file iteration
    validator -- Cerberus
    schema -- the SQL database schema in Python format
    """
    if validator.validate(dict, schema) is not True:
        print ('Validation ERROR!')
        print ('Dictionary = ', dict)
        print ('\nSchema = ', schema)
        print ('\n-------------\n')
        for field, errors in validator.errors.items():
            message_string = "\nElement of type '{0}' has the following errors:\n{1}"
            error_string = pprint.pformat(errors)
            raise Exception(message_string.format(field, error_string))
    return


# ================================================== #
#               Main Function                        #
# ================================================== #

def process_xml_elements(file_in, validate):
    """Iteratively process each XML element tree, build dictionary, validate, and write to CSV files.
    
    Aborts execution if a problem occurs or returns None if successful
    
    Steps through each element in the tree, and calls the function build_dictionary_element_tree 
    to assemble the dictionary
    Sends the dictionary to the validator
    Writes out the dictionary as rows in a CSV file
    Prints a report and returns if successful or aborts if problem occurs
    
    Arguments:
    file_in -- the Open Street Map XML file to process
    validate -- boolean switch to turn on or off validation
    """
    response = fix_it.initialize()
    
    if not response:
        print ('Fatal Error initializing dictionaries')
        print ('\nTerminating execution...')
        return None
        
    with open(NODES_PATH, 'w') as nodes_file, \
         open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
         open(WAYS_PATH, 'w') as ways_file, \
         open(WAY_NODES_PATH, 'w') as way_nodes_file, \
         open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = csv.DictWriter(nodes_file, fieldnames = NODE_FIELDS)
        node_tags_writer = csv.DictWriter(nodes_tags_file, fieldnames = NODE_TAGS_FIELDS)
        ways_writer = csv.DictWriter(ways_file, fieldnames = WAY_FIELDS)
        way_nodes_writer = csv.DictWriter(way_nodes_file, fieldnames = WAY_NODES_FIELDS)
        way_tags_writer = csv.DictWriter(way_tags_file, fieldnames = WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()
        
        print ("\nDATA CORRECTIONS AND ELIMINATIONS\n")

        for element_tree in get_element_tree(file_in, tags=('node', 'way')):
            dict = element_to_dictionary.build_dictionary_element_tree(element_tree)
            if dict:                   # returns False if dict is equal to '0', None', '', False, or empty structure
                fix_it.counts['node way count'] += 1
                if validate is True:
                    validate_dictionary(dict, validator, schema=SCHEMA)

                if element_tree.tag == 'node':
                    fix_it.counts['node count'] += 1
                    nodes_writer.writerow(dict['node'])
                    node_tags_writer.writerows(dict['node_tags'])
                
                elif element_tree.tag == 'way':
                    fix_it.counts['way count'] += 1
                    ways_writer.writerow(dict['way'])
                    way_nodes_writer.writerows(dict['way_nodes'])
                    way_tags_writer.writerows(dict['way_tags'])
                    
            else:
                print ('    -- Dictionary returned is:  ', dict)
    
    print_summary()
    fix_it.print_detailed_fixes(fix_it.counts)
    print ()
    if validate is True:
        print ('Validation... Passed')
    print ('\nCSV files created')
    return

# ================================================================================= #
#               Function to print a report of the process                           #
# ================================================================================= #

def print_summary():
    """Prints a summary report of data corrections and eliminations, and returns None."""
    print ('\n-------')
    print ('SUMMARY')
    print ("\nTag counts:")
    print ("    Nodes: {:,}".format(fix_it.counts['node count']) )
    print ("    Ways: {:,}".format(fix_it.counts['way count']) )
    print ("    Nodes tags: {:,}".format(fix_it.counts['node tag count']) )
    print ("    Ways tags: {:,}".format(fix_it.counts['way tag count']) )
    print ("    Ways Nodes: {:,}".format(fix_it.counts['way node tag count']) )
    
    print ('\nEliminated tag counts:')
    print ("    Tags with bad data values")
    print ('        Nodes tags voided: {:,}'.format(fix_it.counts['node child value eliminated']))
    print ('        Ways tags voided: {:,}'.format(fix_it.counts['way child value eliminated']))
    
    print ('\n    Tags with corrupt ID')
    total = sum(fix_it.node_id_bad.values())
    print ('        Nodes removed: {:,}'.format(total))
    total = sum(fix_it.way_id_bad.values())
    print ('        Ways removed: {:,}'.format(total))
    
    print ("\n    Tags with corrupt keys")
    print ('        Nodes tags with key problem:  {:,}'.format(fix_it.counts['node child key eliminated']))
    print ('        Ways tags with key problem:  {:,}'.format(fix_it.counts['way child key eliminated']))
    
    print ("\n    Tags with defective reference")
    total = sum(fix_it.way_node_reference_bad.values())
    print ('        Ways Nodes tags voided: {:,}'.format(total))
    
    print ("\nSkipped tag counts")
    print ('    Node child tags skipped: {:,}'.format(fix_it.counts['node tag skipped']))
    print ('    Way child tags skipped: {:,}'.format(fix_it.counts['way tag skipped']))
    total = fix_it.counts['node tag skipped'] + fix_it.counts['way tag skipped']
    print ('    Total tags skipped: {:,}'.format(total))
    
    print ( "\nTotal non-node or non-way count: {:,}".format(fix_it.counts['not a node or way count']) )
    print ( "\nTotal elements processed: {:,}".format(fix_it.counts['element count']) )
    return


#========================#
#         Runner         #
#========================#

if __name__ == '__main__':
    # Note: Validation is ~ 10X slower
    # Change validate to validate = True to turn on validation
    process_xml_elements(OSM_PATH, validate = True)  ### CHANGE to True to Validate
