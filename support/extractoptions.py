#!/usr/bin/env python3.3
'''
Prints YAML code for member contact files by parsing HTML web pages.

This script *partially* automates creating member contact YAML files
by extracting form data.  However, be wary of the following:

- Read the web page to verify the output. The parsing is not
  guaranteed to be correct.

- Ignore extraneous output.  The script parses all <input> tags to be
  safe and not miss anything.
  
- Single quoted attributes don't work out of the box.  To parse them,
  change the regex at the start of the script to:

    selectoptions: r'(?:<option.*?value\s*=\s*)(\'.*?\')'
    inputname: r'(?:<input.*?name\s*=\s*\')(.*?)(?:\')'
    inputselectors: r'(?:<input.*?id\s*=\s*\')(.*?)(?:\')'

Usage
=====

Save contact HTML forms into an 'input/' folder.

Best practise is to only copy the HTML containing the form that you
want to extract, as opposed to the entire HTML source code.  Using the
entire source works, but may be more error prone than using a limted
selection.

To extract a limited selection in Mozilla Firefox, open Tools > Web
Developer > Inspector.  Mouse over the page till you enclose the
contact form (a good place to start is the title of the form).  In the
page source of the Inspector tool, right-click on the highlighted tag
level and choose "Copy Inner HTML".  Save your clipboard contents into
a new text file in the 'input/' folder (the filename extension is
irrelevant as the script parses all files in the 'input/' folder).
'''

import os
import re

# If set True, prints "required: " attribute for fields that are not
# required.
ALLOW_EMPTY_REQUIRED = False

YAMLselections = []

#compile regular expressions
#select = re.compile(r'<select.*?</select>', re.DOTALL | re.IGNORECASE)
selectoptions = re.compile(r'(?:<option.*?value\s*=\s*\")(.*?)(?:\")', re.IGNORECASE)
selecttext = re.compile(r'(?:<option.*?value.*?>)(.*?)(?:</)', re.IGNORECASE)
inputname = re.compile(r'(?:<input.*?name\s*=\s*\")(.*?)(?:\")', re.IGNORECASE)
inputselectors = re.compile(r'(?:<input.*?id\s*=\s*\")(.*?)(?:\")', re.IGNORECASE)
for root,dirs,files in os.walk('input'):
    for file in files:
        with open('input' + os.sep + file, 'r') as f:
            html = f.read()
        #limit by form
        #input search
        data = '------------\n' + file + '\n' + 'inputs:' + '\n'
        inputs = re.findall(inputname, html)
        selectors = re.findall(inputselectors, html)
        data = data + "    " + "- fill_in:\n"
        for i in range(0,len(inputs)):
            try: 
                data = data + "      " + "- name: " + inputs[i] + "\n"
                data = data + "        " + "selector: \"#" + selectors[i] + "\"\n"
                data = data + "        " + "value: "
                if inputs[i].find("first") != -1:
                    data = data + "$NAME_FIRST\n"
                elif inputs[i].find("last") != -1:
                    data = data + "$NAME_LAST\n"
                elif inputs[i].find("zip5") != -1:
                    data = data + "$ADDRESS_ZIP5\n"
                elif inputs[i].find("zip4") != -1:
                    data = data + "$ADDRESS_ZIP4\n"
                elif inputs[i].find("prefix") != -1:
                    data = data + "$NAME_PREFIX\n"
                elif inputs[i].find("address2") != -1:
                    data = data + "$ADDRESS_STREET_2\n"
                elif inputs[i].find("address") != -1:
                    data = data + "$ADDRESS_STREET\n"
                elif inputs[i].find("city") != -1:
                    data = data + "$ADDRESS_CITY\n"
                elif inputs[i].find("state") != -1:
                    data = data + "$ADDRESS_STATE_POSTAL_ABBREV\n"
                elif inputs[i].find("email") != -1:
                    data = data + "$EMAIL\n"
                elif inputs[i].find("phone") != -1:
                    data = data + "$PHONE\n"
                elif inputs[i].find("subject") != -1:
                    data = data + "$SUBJECT\n"
                elif inputs[i].find("message") != -1:
                    data = data + "$MESSAGE\n"
                else:
                    data = data + "\n"
                if inputs[i].find("required") != -1:
                    data = data + "        " + "required: Yes\n"
                elif ALLOW_EMPTY_REQUIRED:
                    data = data + "        " + "required: \n"
            except IndexError:
                data = data + "\ninputs may not match selectors\n"
        data = data + "      " + "- name: \n" + "        " + "selector: \"#\n" + "        " + "value: \n" + "        " + "required: \n"
        #option search
        options = re.findall(selectoptions, html)
        text = re.findall(selecttext, html)
        data = data + '------------\n' + file + '\n' + 'options:' + '\n'
        if len(options) != len(text):
            data = data + "\nerror with text, printing option values only\n"
            for option in options:
                data = data + "          "
                data = data + "- \"" + option + "\"\n"
            YAMLselections.append(data)
        elif set(options) != set(text):
            data = data + "\noptions != text, printing hash\n"
            for i in range(0,len(options)):
                data = data + "          "
                data = data + "\"" + text[i] + "\":" + " \"" + options[i] + "\"\n"
            YAMLselections.append(data)
        else:
            for option in options:
                data = data + "          "
                data = data + "- \"" + option + "\"\n"
            YAMLselections.append(data)
            
for x in YAMLselections:
    print(x)
