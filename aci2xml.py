
# 
# Copyright (c) 2015 Fluke Networks.
# All rights reserved.
# No part of this source code may be copied, used, or modified
# without the express written consent of Fluke Networks.
# 
# aci2xml.py: Convert the policy manager related section in a *.aci
# file to xml. For example, these lines:

    # [\PolicyManager\Alarm0]
	    # Enable=D_1
	    # Count_Of_Threshold=D_1
    # [\PolicyManager\Alarm0\Threshold0]
	    # Severity=D_2
	    # SeverityScore=D_100
	    # Action=S_Beep
	    # GroupType=D_2
	    # SSIDGroupCount=D_1
	    # SSIDGroup=S_MyWLAN
	    # ACLGroupCount=D_2
	    # ACLGroups=S_0,1

# Will be converted to this:

	# <Alarm0>
		# <AlarmEnabled>1</AlarmEnabled>
		# <ThresholdCount>1</ThresholdCount>
		# <Threshold0>
			# <Severity>2</Severity>
			# <Action>Beep</Action>
			# <ThresholdInt>0</ThresholdInt>
			# <ThresholdString/>
			# <GroupType>2</GroupType>
			# <IntArray_Count>0</IntArray_Count>
			# <IntArray/>
			# <FrameCount>50</FrameCount>
			# <SignalStrength>15</SignalStrength>
			# <IntMap_Count>0</IntMap_Count>
			# <IntMap/>
			# <SSIDGroups_Count>1</SSIDGroups_Count>
			# <SSIDGroups>MyWLAN</SSIDGroups>
			# <ACLGroups_Count>1</ACLGroups_Count>
			# <ACLGroups>0</ACLGroups>
		# </Threshold0>
	# </Alarm0>

import os, argparse
import json
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import tostring
import xml.dom.minidom as minidom

def dictToXmlElement(tag, xmlDict):
    '''
    Convert a dict to xml element
    '''
    if not xmlDict or not isinstance(xmlDict, dict):
        return None
    elem = Element(tag)
    for key, val in xmlDict.items():
        if isinstance(val, dict):
            # The next level is also a dict. recursive call to convert any depth
            child = dictToXmlElement(key, val)
        else:
            child = Element(key)
            child.text = str(val)
        elem.append(child)
    return elem

def readAci(fileName):
    xmlRoot = dict()
    with open(fileName) as f:
        currNode = None
        for s in f:
            s = s.strip()
            #print s
            if s.startswith('[\\') and s.endswith(']'):
                s = s[1:-1].strip()
                if s == "":
                    currNode = None
                    continue
                xmlKeys = s.split('\\')
                currNode = xmlRoot
                for key in xmlKeys:
                    if key == "":
                        continue
                    if not key in currNode:
                        currNode[key] = dict()
                    currNode = currNode[key]
            elif '=' in s:
                if currNode == None:
                    print s
                else:
                    pos = s.find('=')
                    key = s[0:pos]
                    value = s[pos+3:]
                    currNode[key] = value
    
    return xmlRoot
    
def writePolicyManagerXml(xmlDict, fileName):
    '''
    COnvert a simple dict from reading aci file to xml tree
    '''
    if 'PolicyManager' in xmlDict:
        xmlElem = dictToXmlElement('PolicyManager', xmlDict['PolicyManager'])
        xmlString = tostring(xmlElem)
        reparsed = minidom.parseString(xmlString)
        with open(fileName, 'wb') as f:
            reparsed.writexml(f, indent="\t", addindent="\t", newl="\n")
            print 'Policy written to:',  fileName

def main():
    #parser = argparse.ArgumentParser(description='Convert the policy manager related section in a .aci file to xml file.')
    #parser.add_argument('aciFile', type=str, help='ACI file name', nargs='?', default='./config/Default.aci')
    #parser.add_argument('xmlFile', type=str, help='XML file name', nargs='?', default='./config/Default.xml')

    #args = parser.parse_args()
    
    aciFile = './config/Default.aci'
    xmlFile = './config/Default.xml'

    print 'Converting', aciFile, '->', xmlFile
    xmlDict = readAci(aciFile)
    if not xmlDict:
        print 'Can not open the xml file or it is empty:', xmlFile
    writePolicyManagerXml(xmlDict, xmlFile)
    print 'Done!'

if __name__ == '__main__':
    main()
