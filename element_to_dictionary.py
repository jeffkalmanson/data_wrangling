# Filename: element_to_dictionary.py
# Python 3.7
# Notes:
#    This is a module of main_process.py
#    Not to be run independently -- Use 'python main_process.py'
# Purpose: Convert the element to a dictionary

# Each element in the XML file is sent here to the "build_dictionary_element" function.
# The element is examined and for each child in the element, the child 'value' is sent
#   to the "fix_it" function (in file "fix_it.py") for correcting.
# A Python dictionary is constructed and returned back to the "process_xml_elements" function
#   (in file "main_process.py") for writing into the csv files.

import pprint
import re
import xml.etree.cElementTree as ET

import fix_it

#========================================================#
#     Define regular expression and initialize lists     #
#========================================================#

correct_chars_re = re.compile(r"^[a-zA-Z:\-_1-9]+$")

# Be sure the field order in the csv files matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']

# ==================================================== #
#               Helper Function                        #
# ==================================================== #

def check_id(id):
    """Helper function to check the ID, and returns it or None if the ID is corrupt.
    
    Arguments:
    id -- the ID number attribute of the element tags <node> or <way>
    """
    id = id.strip()
    
    if id and id.isdigit():   # id must only be a number
        return id
    else:
        return None

# ================================================================= #
#       Function to build a dictionary from the element tree        #
# ================================================================= #


def build_dictionary_element_tree(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                                  default_tag_type='regular'):
    """Function takes an iterparse Element object (element tree) as an input and returns a dictionary.
    
    Checks ID, key and reference
    Sends children <tags> to the function fix_it for data value correction or elimination
    Saves <node> or <way> XML element tree to a Python dictionary
    
    Arguments:
    element -- the current element tree in the XML file iteration
    node_attr_fields -- list of attributes for <node> tag
    way_attr_fields -- list of attributes for <way> tag
    default_tag_type -- set to 'regular'
    """
    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []           # Handle secondary tags the same way for both node and way elements
    
    if element == None:
        print ('Element is Null')
        return None
    
    if element.tag == 'node':
        check = check_id(element.attrib['id'])
        
        if not check:
            print ('Node ID is Null or not a number: ', element.attrib['id'])
            fix_it.node_id_bad[element.attrib['id']] += 1
            return None
        
        for attr in element.attrib:
            if attr in node_attr_fields:
                node_attribs[attr] = element.attrib[attr]
        
        for child in element:
            temp = { }
            
            if 'cityracks.' in child.attrib['k']:
                child.attrib['k'] = child.attrib['k'].replace('cityracks.','')
                   
            m = correct_chars_re.search(child.attrib['k'])    # No match returns None

            if not m:    
                print ('Node key -- Problem character!   ', 'key =  ', child.attrib['k'], '   value =  ', child.attrib['v'])
                fix_it.counts['node child key eliminated'] += 1
                infoKey = 'node key: ' + child.attrib['k']
                fix_it.bad_keys[infoKey] += 1
                continue      # eliminate the problematic child tag
            
            # Fix value
            fixed = fix_it.fixer(child, 'Node')       # Correct or eliminate the child <tag> value
                                                # Function fix_it returns None if there is a data problem
            if fixed == '$skip':
                fix_it.counts['node tag skipped'] += 1
                continue
            
            if not fixed:
                fix_it.counts['node child value eliminated'] += 1
                continue                 # Eliminate this child tag
            else:
                temp['id'] = element.attrib['id']     # Save the fixed child tag for writing into csv file
                temp['value'] = fixed
            
            if ':' in child.attrib['k']:
                k = child.attrib['k'].split(':',1)
                temp['type'] = k[0]
                temp['key'] = k[1]
            else:
                temp['key'] = child.attrib['k']
                temp['type'] = default_tag_type
            
            fix_it.counts['node tag count'] += 1     # count the child tags not eliminated
            tags.append(temp)
        
        return {'node': node_attribs, 'node_tags': tags}
    
    elif element.tag == 'way':
        check = check_id(element.attrib['id'])
        
        if not check:
            print ('Way ID is Null or not a number: ', element.attrib['id'])
            fix_it.way_id_bad[element.attrib['id']] += 1
            return None
        
        for attr in element.attrib:  
            if attr in way_attr_fields:
                way_attribs[attr] = element.attrib[attr]
        
        position = 0
        for child in element:
            temp = { }
            
            if child.tag == 'tag':
                m = correct_chars_re.search(child.attrib['k'])    # No match returns None
                
                if not m:
                    print ('Way key -- Problem char!   ', 'key =  ', child.attrib['k'], '   value =  ', child.attrib['v'])
                    fix_it.counts['way child key eliminated'] += 1
                    infoKey = 'way key: ' + child.attrib['k']
                    fix_it.bad_keys[infoKey] += 1
                    continue     # eliminate the problematic child tag
                
                # Fix value
                fixed = fix_it.fixer(child, 'Way')        # Correct or eliminate the child <tag> value
                                             # Function fix_it returns None if there is a data problem
                if fixed == '$skip':
                    fix_it.counts['way tag skipped'] += 1
                    continue
                
                if not fixed:
                    fix_it.counts['way child value eliminated'] += 1
                    continue                 # Eliminate this child tag
                else:
                    temp['id'] = element.attrib['id']     # Save the fixed child tag for writing into csv file
                    temp['value'] = fixed

                if ':' in child.attrib['k']:
                    k = child.attrib['k'].split(':',1)
                    temp['type'] = k[0]
                    temp['key'] = k[1]
                else:
                    temp['key'] = child.attrib['k']
                    temp['type'] = default_tag_type
                
                fix_it.counts['way tag count'] += 1     # count the child tags not eliminated
                tags.append(temp)
            
            elif child.tag == 'nd':
                check = check_id(child.attrib['ref'])
                
                if not check:
                    print ('Way Node reference is Null or not a number: ', child.attrib['ref'])
                    fix_it.way_node_reference_bad[child.attrib['ref']] += 1
                    continue
                
                temp['id'] = element.attrib['id']
                temp['node_id'] = child.attrib['ref']
                temp['position'] = position
                position += 1
                fix_it.counts['way node tag count'] += 1     # count the child tags not eliminated
                way_nodes.append(temp)
        
        #print ('way_attribs:\n', way_attribs)
        #print ('way_nodes:\n', way_nodes)
        #print ('way_tags:\n', tags)
        #print ('---------------\n')
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}
