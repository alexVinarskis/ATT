import os
import xml.etree.ElementTree as ET
import re
import boto3
from sys import platform

################################################################################
#
# Modified AWS translate program
# additional features:
# 1. Auto scan value-XX folders for strings.xml
# 2. IGNORES LOCALES (eg pt-BT & pt-PT)
#
################################################################################

# run via 

# PYTHONIOENCODING=utf8 python3 AWS_translate.py OR using pythong launcher 
# follow instructions

# P.S. You must have AWS CLI installed and configure on the machine!
# edited by alexVinrskis, March 2020

################################################################################
# 
# Funcion: XML file translator
#
# Gets input .xml, and translates it
# Does NOT override, if output string exists!
#
# ADDITION ONLY
#
################################################################################

def xmlTranlator(INPUTLANGUAGE, OUTPUTLANGUAGE, fIn, fOut, extra_strings):
    root_out = ET.parse(fOut).getroot()
    root_in = ET.parse(fIn).getroot()

    attrs_out = []
    for element in root_out:
        attrs_out.append(element.attrib.get('name'))
  
    counter = 0
    newRoot = ET.Element('resources')
    to_change_list = []
    to_change_list_names = []

    for root_element in root_in:
        if (root_element.attrib.get('name') not in attrs_out or root_element.attrib.get('name') in extra_strings) and root_element.get('translatable') != 'false':
            # translate elemenet(s)
            if root_element.tag=='string':
                # trasnalte text and fix any possible issues traslotor creates: messing up HTML tags, adding spaces between string formatting elements
                totranslate=root_element.text
                # if single string - translate directly
                if totranslate!=None:
                    root_element.text=translate.translate_text(Text=totranslate, SourceLanguageCode=INPUTLANGUAGE, TargetLanguageCode=OUTPUTLANGUAGE).get('TranslatedText').replace('\\ ', '\\').replace('\\ n ', '\\n').replace('\\n ', '\\n').replace('/ ', '/').replace("\'", "\\'")

                # if string was broken down due to HTML tags, reassemble it
                # if string has subelements, previous command will fail - do by parts reconstruction
                if len(root_element) != 0:
                    for element in range(len(root_element)):
                        if root_element[element].text != None:
                            root_element[element].text = " " + translate.translate_text(Text=root_element[element].text, SourceLanguageCode=INPUTLANGUAGE, TargetLanguageCode=OUTPUTLANGUAGE).get('TranslatedText').replace('\\ ', '\\').replace('\\ n ', '\\n').replace('\\n ', '\\n').replace('/ ', '/').replace("\'", "\\'")
                        if root_element[element].tail != None:
                            root_element[element].tail = " " + translate.translate_text(Text=root_element[element].tail, SourceLanguageCode=INPUTLANGUAGE, TargetLanguageCode=OUTPUTLANGUAGE).get('TranslatedText').replace('\\ ', '\\').replace('\\ n ', '\\n').replace('\\n ', '\\n').replace('/ ', '/').replace("\'", "\\'")

            if root_element.tag=='string-array':
                for j in range(len(root_element)):
                #	for each translatable string call the translation subroutine
                #   and replace the string by its translation,
                    if root_element[j].tag=='item':
                        # trasnalte text and fix any possible issues traslotor creates: messing up HTML tags, adding spaces between string formatting elements
                        totranslate=root_element[j].text
                        if(totranslate!=None):
                            root_element[j].text=translate.translate_text(Text=totranslate, SourceLanguageCode=INPUTLANGUAGE, TargetLanguageCode=OUTPUTLANGUAGE).get('TranslatedText').replace('\\ ', '\\').replace('\\ n ', '\\n').replace('\\n ', '\\n').replace('/ ', '/').replace("\'", "\\'")

                        # if string was broken down due to HTML tags, reassemble it
                        if len(root_element[j]) != 0:
                            for element in range(len(root_element[j])):
                                if root_element[j][element].text != None:
                                    root_element[j][element].text = " " + translate.translate_text(Text=root_element[j][element].text, SourceLanguageCode=INPUTLANGUAGE, TargetLanguageCode=OUTPUTLANGUAGE).get('TranslatedText').replace('\\ ', '\\').replace('\\ n ', '\\n').replace('\\n ', '\\n').replace('/ ', '/').replace("\'", "\\'")
                                if root_element[j][element].tail != None:
                                    root_element[j][element].tail = " " + translate.translate_text(Text=root_element[j][element].tail, SourceLanguageCode=INPUTLANGUAGE, TargetLanguageCode=OUTPUTLANGUAGE).get('TranslatedText').replace('\\ ', '\\').replace('\\ n ', '\\n').replace('\\n ', '\\n').replace('/ ', '/').replace("\'", "\\'")

            # add element to tree, or save to overwrite it (without breaking order)
            if root_element.attrib.get('name') in extra_strings:
                to_change_list.append(root_element)
                to_change_list_names.append(root_element.attrib.get('name'))
            else:
                newRoot.append(root_element)

            if useDebug: 
                print("adding: ", root_element.attrib)

            counter = counter + 1
    
    # edit elements which already existed, and were manually overwritten - preserves the order
    for i in range(len(root_out)):
        if root_out[i].attrib.get('name') in to_change_list_names:
            root_out[i] = to_change_list[to_change_list_names.index(root_out[i].attrib.get('name'))]

    root_out.extend(newRoot)
    ET.ElementTree(root_out).write(fOut, encoding='utf-8')
    print('Added ' , counter, ' element(s) to ', OUTPUTLANGUAGE)

################################################################################
#
# MAIN PROGRAM
#
################################################################################

print("=================================================\n")

# connect to AWS 
translate = boto3.client(service_name='translate', region_name='eu-west-1', use_ssl=True)

# prepare
pathSeparator = ""
if platform == "linux" or platform == "linux2":
    # linux (like mac??)
    pathSeparator = "/"
elif platform == "darwin":
    # OS X
    pathSeparator = "/"
elif platform == "win32":
    # Windows...
    pathSeparator = "\\"

# get systems paths
pathRes = "app" + pathSeparator + "src" + pathSeparator + "main" + pathSeparator + "res"

################################################################################
#
# STRINGS SUBPROGRAM
#
################################################################################

# setting vars
useDebug = False
xmlSubfolder = 'values'
xmlResource = 'strings.xml'
xmlSubfolderInput = ''
xmlLangIn = ''          # default lang to take as translation source; empty means DEFAULT=ENGLISH
xmlAutoComplete = True  # check if any existing lang is missing string - ADD them
xmlAddLangs = ''        # add new language(s)

# get input lang
while xmlLangIn == '':
    xmlLangIn = input("Enter SOURCE language for strings.xml\nType 'default' to use default; Default MUST be english\n").lower()
    # check that input settings are valid - XML source files exist
    strings_in = ''
    if xmlLangIn == 'default':
        strings_in = pathRes + pathSeparator + xmlSubfolder + pathSeparator + xmlResource
        if not os.path.exists(strings_in):
            print("ERROR: no default .XML; App's default strings.xml must be in English\n")
            xmlLangIn = ''
        xmlSubfolderInput = xmlSubfolder
    elif xmlLangIn == '':
        print("You must explicitly confirm which 'values' folder to use as source\n")
    else:
        strings_in = pathRes + pathSeparator + xmlSubfolder + "-" + xmlLangIn + pathSeparator + xmlResource
        if not os.path.exists(strings_in):
            print("ERROR: no .XML resource for selected source language\n")
            xmlLangIn = ''
        xmlSubfolderInput = xmlSubfolder + "-" + xmlLangIn

askUseDebug = input("\nDetailed logs? [Y/N (Default)]\n").lower()
if askUseDebug == 'y':
    useDebug = True

overwrite_strings = input("\nAny strings to overwrite from source? Specify tags space separated\n").lower().split()
print('\n')

# get list of strings folders
files_all = os.listdir(pathRes)
values_folders = []
values_languages = []
for file in files_all:
    if file != xmlSubfolderInput and re.match(r"values-[a-zA-Z]{2}\b", file):
        values_folders.append(file)
        values_languages.append(file[-2:])
if xmlLangIn != 'default':
    values_folders.append(xmlSubfolder)
    values_languages.append('en')
else:
    xmlLangIn = 'en'

# iterate each file & identify missing strings & sync them
for i in range(len(values_folders)):
    strings_out = pathRes + pathSeparator + values_folders[i] + pathSeparator + xmlResource
    xmlTranlator(xmlLangIn, values_languages[i], strings_in, strings_out, overwrite_strings)

print("\n=================================================\n\n")
