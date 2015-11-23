"""
Surveyor - Canvas API Organizer - Open Source
By: Megg Gawat, 2015

---Structure---
Classes:
    Login(username, password) - Requires username and password, creates a login object
    Forms_API(login_obj) - Requires a login object, uses the Canvas forms api 
        count_forms() - Counts the total number of forms on the account
        list_forms() - lists all the forms available in the account, output: name, id
    Submissions_API(login_obj, formid) - Utilizes the Canvas Submissions API

---How To Use---
1) You must first instanstiate a login object
2) You must then use that login object to instanstiate a CanvasXML object


Ideas:
App that counts all the answers
App that can store old submission values into a reference data, so it shows up next time the app is opened
"""

import urllib2 #Used for accessing the canvas apiss
import xml.etree.ElementTree as ET #for reading XML files
import webbrowser #used for opening links in web browser
import abc #abstract base class
import collections #for ordered dict

class Login(object):
    def __init__(self, username=None, password=None):
        if username == None:
            username = raw_input('Enter username: ')
        if password == None:
            password = raw_input('Enter password: ')
        username = username.replace('+', '%2B') #URL Encoding
        self.username = username
        self.password = password

class Canvas_API(object):

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self, login_obj):
        username = '?username=' + login_obj.username
        password = '&password=' + login_obj.password
        self.api_call = self.api_url + username + password
        self.api_xml = urllib2.urlopen(self.api_call).read() #The XML source code stored into a string

    def visit_api(self):
        """Opens the XML file in the web browser"""
        webbrowser.open(self.api_call)

class Forms_API(Canvas_API):

    def __init__(self, login_obj):
        self.api_url = 'https://www.gocanvas.com/apiv2/forms.xml'
        super(Forms_API, self).__init__(login_obj)

    def list_forms(self):
        root = ET.fromstring(self.api_xml)
        for label in root.iter('Form'):
            print(label.getchildren()[0].text + ' -- ID: ' + label.attrib['Id'] + ' -- Version: ' + label.getchildren()[2].text + ' -- Status: ' + label.getchildren()[1].text)

    def count_forms(self):
        root = ET.fromstring(self.api_xml)
        total_forms = 0
        for form in root.iter('Form'):
            total_forms += 1
        return total_forms

class Submissions_API(Canvas_API):

    def __init__(self, login_obj, formid):
        self.api_url = 'https://www.gocanvas.com/apiv2/submissions.xml'
        super(Submissions_API, self).__init__(login_obj)
        self.api_call = self.api_call + '&form_id=' + str(formid)
        self.api_xml = urllib2.urlopen(self.api_call).read()
        # openedxml = open('test.txt', 'r')
        # self.api_xml = openedxml.read()

    def count_responses(self):
        root = ET.fromstring(self.api_xml)
        dict_of_fields = collections.OrderedDict()
        for response in root.iter('Response'):
            """This loop creates a dictionary of all fields, and a dictionary of all answers, then counts how many times that answer occurs"""
            label = response.getchildren()[0].text
            value = response.getchildren()[1].text
            if label not in dict_of_fields:
                dict_of_fields[label] = collections.OrderedDict()
            if value not in dict_of_fields[label]:
                if value == None:
                    dict_of_fields[label]['Left Blank'] = 0
                if value != None:
                    dict_of_fields[label][value] = 0
            if value == None:
                dict_of_fields[label]['Left Blank'] += 1
            if value != None:
                dict_of_fields[label][value] += 1
        for label in dict_of_fields:
            """This loop displays the dictionary in a logical format"""
            print('---' + label + '---')
            for value in dict_of_fields[label]:
                print(value + ': ' + str(dict_of_fields[label][value]))
            print('')
