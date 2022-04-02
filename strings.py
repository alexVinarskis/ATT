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

def xmlTranlator(INPUTLANGUAGE, OUTPUTLANGUAGE, fIn, fOut):
    root_out = ET.parse(fOut).getroot()
    root_in = ET.parse(fIn).getroot()

    attrs_out = []
    for element in root_out:
        attrs_out.append(element.attrib)

    counter = 0
    newRoot = ET.Element('resources')

    for element in root_in:
        if element.attrib not in attrs_out and element.get('translatable') != 'false':
            # translate elemenet(s)
            if element.tag=='string':
                # trasnalte text and fix any possible issues traslotor creates: messing up HTML tags, adding spaces between string formatting elements
                totranslate=element.text
                # if single string - translate directly
                if(totranslate!=None):
                    element.text=translate.translate_text(Text=totranslate, SourceLanguageCode=INPUTLANGUAGE, TargetLanguageCode=OUTPUTLANGUAGE).get('TranslatedText').replace('\\ ', '\\').replace('\\ n ', '\\n').replace('\\n ', '\\n').replace('/ ', '/').replace("\'", "\\'")

                # if string was broken down due to HTML tags, reassemble it
                # if string has subelements, previous command will fail - do by parts reconstruction
                if len(element) != 0:
                    for element in range(len(element)):
                        if element[element].text != None:
                            element[element].text = " " + translate.translate_text(Text=element[element].text, SourceLanguageCode=INPUTLANGUAGE, TargetLanguageCode=OUTPUTLANGUAGE).get('TranslatedText').replace('\\ ', '\\').replace('\\ n ', '\\n').replace('\\n ', '\\n').replace('/ ', '/').replace("\'", "\\'")
                        if element[element].tail != None:
                            element[element].tail = " " + translate.translate_text(Text=element[element].tail, SourceLanguageCode=INPUTLANGUAGE, TargetLanguageCode=OUTPUTLANGUAGE).get('TranslatedText').replace('\\ ', '\\').replace('\\ n ', '\\n').replace('\\n ', '\\n').replace('/ ', '/').replace("\'", "\\'")

            if element.tag=='string-array':
                for j in range(len(element)):
                #	for each translatable string call the translation subroutine
                #   and replace the string by its translation,
                    isTranslatable=element[j].get('translatable')
                    if(element[j].tag=='item') & (isTranslatable!='false'):
                        # trasnalte text and fix any possible issues traslotor creates: messing up HTML tags, adding spaces between string formatting elements
                        totranslate=element[j].text
                        if(totranslate!=None):
                            element[j].text=translate.translate_text(Text=totranslate, SourceLanguageCode=INPUTLANGUAGE, TargetLanguageCode=OUTPUTLANGUAGE).get('TranslatedText').replace('\\ ', '\\').replace('\\ n ', '\\n').replace('\\n ', '\\n').replace('/ ', '/').replace("\'", "\\'")

                        # if string was broken down due to HTML tags, reassemble it
                        if len(element[j]) != 0:
                            for element in range(len(element[j])):
                                if element[j][element].text != None:
                                    element[j][element].text = " " + translate.translate_text(Text=element[j][element].text, SourceLanguageCode=INPUTLANGUAGE, TargetLanguageCode=OUTPUTLANGUAGE).get('TranslatedText').replace('\\ ', '\\').replace('\\ n ', '\\n').replace('\\n ', '\\n').replace('/ ', '/').replace("\'", "\\'")
                                if element[j][element].tail != None:
                                    element[j][element].tail = " " + translate.translate_text(Text=element[j][element].tail, SourceLanguageCode=INPUTLANGUAGE, TargetLanguageCode=OUTPUTLANGUAGE).get('TranslatedText').replace('\\ ', '\\').replace('\\ n ', '\\n').replace('\\n ', '\\n').replace('/ ', '/').replace("\'", "\\'")

            # add element to tree
            newRoot.append(element)
            counter = counter + 1

            if useDebug: 
                print("adding: ", element.attrib)

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

askUseDebug = input("\nDetailed logs? [Y/N (Default)] ").lower()
if askUseDebug == 'y':
    useDebug = True
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
    xmlTranlator(xmlLangIn, values_languages[i], strings_in, strings_out)

print("\n=================================================\n\n")
