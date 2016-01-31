"""
Surveyor - Canvas API Organizer - Open Source
Python3 Version
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

import urllib.request, urllib.error, urllib.parse #Used for accessing the canvas apiss
import xml.etree.ElementTree as ET #for reading XML files
import webbrowser #used for opening links in web browser
import abc #abstract base class
import collections #for ordered dict
import tkinter #used for gui
import tkinter.scrolledtext as tkst #used for gui textboxes with scrollbars

class Login(object):
    def __init__(self, username, password):
        username = username.replace('+', '%2B') #URL Encoding
        self.username = username
        self.password = password

class Canvas_API(object, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __init__(self, login_obj):
        username = '?username=' + login_obj.username
        password = '&password=' + login_obj.password
        self.api_call = self.api_url + username + password
        self.api_xml = urllib.request.urlopen(self.api_call).read() #The XML source code stored into a string

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
            print((label.getchildren()[0].text + ' -- ID: ' + label.attrib['Id'] + ' -- Version: ' + label.getchildren()[2].text + ' -- Status: ' + label.getchildren()[1].text))

    def count_forms(self):
        root = ET.fromstring(self.api_xml)
        total_forms = 0
        for form in root.iter('Form'):
            total_forms += 1
        print(total_forms)
        return total_forms

    def verify_login(self):
        #Verifies if the login works by opening the XML file, and if the first child of the root is "Error", it is a failed login. If it works, it should be "Forms".
        verifyroot = ET.fromstring(self.api_xml)
        if verifyroot[0].tag == "Error":
            return False
        return True

class Submissions_API(Canvas_API):
    def __init__(self, login_obj, formid):
        self.api_url = 'https://www.gocanvas.com/apiv2/submissions.xml'
        super(Submissions_API, self).__init__(login_obj)
        self.api_call = self.api_call + '&form_id=' + str(formid)
        self.api_xml = urllib.request.urlopen(self.api_call).read()
        # openedxml = open('test.txt', 'r')
        # self.api_xml = openedxml.read()

    def tally_responses(self):
        root = ET.fromstring(self.api_xml)
        dict_of_screens = collections.OrderedDict()

        """Populates the dict_of_screens dictionary with information about the form"""
        for screen in root.iter('Screen'):
            screen_name = screen.getchildren()[0].text
            if screen_name not in dict_of_screens:
                dict_of_screens[screen_name] = collections.OrderedDict()
            for response in screen.iter('Response'):
                field = response.getchildren()[0].text
                value = response.getchildren()[1].text
                if field not in dict_of_screens[screen_name]:
                    dict_of_screens[screen_name][field] = collections.OrderedDict()
                if str(value) not in dict_of_screens[screen_name][field]:
                    if value == None:
                        dict_of_screens[screen_name][field]['None'] = 0 
                    if value != None: 
                        dict_of_screens[screen_name][field][value] = 0 
                if value == None: 
                    dict_of_screens[screen_name][field]['None'] += 1 
                if value != None: 
                    dict_of_screens[screen_name][field][value] += 1 
                            
        """Displays the dict_of_screens dictionary in a readable format""" 
        for screen in dict_of_screens: 
            print('') 
            print(('~~**~~ ' + screen + ' ~~**~~')) 
            for label in dict_of_screens[screen]: 
                print('') 
                print(label) 
                print('----------') 
                for value in dict_of_screens[screen][label]: 
                    print((value + ': ' + str(dict_of_screens[screen][label][value]))) 
            print('')

class Images_API(Canvas_API):
    def __init__(self, login_obj, image_id):
        self.api_url = 'https://www.gocanvas.com/apiv2/images.xml'
        super(Images_API, self).__init__(login_obj)
        self.api_call = self.api_call + '&image_id=' + str(image_id)

class Reference_Data_API(Canvas_API):
    def __init__(self, login_obj):
        self.api_url = 'https://www.gocanvas.com/apiv2/reference_datas'
        super(Reference_Data_API, self).__init__(login_obj)

class CSV_Meta_Data_API(Canvas_API):
    def __init__(self, login_obj, form_id):
        self.api_url = 'https://www.gocanvas.com/apiv2/csv_meta_datas.xml'
        super(CSV_Meta_Data_API, self).__init__(login_obj)
        self.api_call = self.api_call + '&form_id=' + str(form_id)
        self.api_xml = urllib.request.urlopen(self.api_call).read()
        print(self.api_xml)

    def list_submissions(self):
        #To Do: List Form ID + Version + How many submission + current status
        pass

class CSV_API(Canvas_API):
    def __init__(self, login_obj):
        pass

class Dispatch_Items_API(Canvas_API):
    pass

class Submissions_Push_Notifications_API(Canvas_API):
    pass

class SurveyorInterface(object):
    def __init__(self, master):
        self.master = master
        self.master.title("Canvas Toolkit")
        self.mainframe = tkinter.Frame(master)
        self.mainframe.pack(padx=10, pady=10)

        self.username = tkinter.StringVar()
        self.password = tkinter.StringVar()
        self.submissions_form_id = tkinter.StringVar()
        self.images_form_id = tkinter.StringVar()
        self.meta_form_id = tkinter.StringVar()
        self.console_text = tkinter.StringVar()

        self.build_login_gui()

    def build_login_gui(self):
        self.login_frame = tkinter.Frame(self.mainframe)
        self.login_frame.grid(row = 0, column = 0)

        canvas_toolkit_title = tkinter.Label(self.login_frame, text="Canvas Toolkit")
        canvas_toolkit_title.grid(column = 0, row = 0, columnspan = 2)

        username_text = tkinter.Label(self.login_frame, text = "Username")
        username_text.grid(column = 0, row = 1)
        username_box = tkinter.Entry(self.login_frame, textvariable = self.username)
        username_box.grid(column = 0, row = 2)

        password_text = tkinter.Label(self.login_frame, text = "Password")
        password_text.grid(column = 1, row = 1)
        password_box = tkinter.Entry(self.login_frame, textvariable = self.password, show="*")
        password_box.grid(column = 1, row = 2)

        login_button = tkinter.Button(self.login_frame, text="Login", command = self.attempt_login)
        login_button.grid(column = 0, row = 4, columnspan = 2, pady=5)

    def attempt_login(self):
        self.account_info = Login(self.username.get(), self.password.get())
        self.forms_api_login = Forms_API(self.account_info)
        self.ref_api_login = Reference_Data_API(self.account_info)

        if self.forms_api_login.verify_login() == True:
            self.login_frame.grid_forget()
            self.build_forms_browser()
            self.build_console()
            self.build_buttons_kit()
        else:
            incorrect_login_message = tkinter.Label(self.login_frame, text = "Error: Incorrect Login")
            incorrect_login_message.grid(column = 0, row = 3, columnspan = 2)
            #Commented the above to make it easier to log in and test, otherwise remove in final versoin
            #self.login_frame.grid_forget()
            #self.build_forms_browser()
            #self.build_console()
            #self.build_buttons_kit()

    def build_forms_browser(self):
        forms_browser_frame = tkinter.Frame(self.mainframe)
        forms_browser_frame.grid(column = 0, row = 1)        

    def build_console(self):
        console_frame = tkinter.Frame(self.mainframe)
        console_frame.grid(column = 0, row = 2)

    def build_buttons_kit(self):
        buttons_kit_frame = tkinter.Frame(self.mainframe)
        buttons_kit_frame.grid(column = 0, row = 3)

        #-----Forms API Buttons-----#

        forms_api_title = tkinter.Label(buttons_kit_frame, text = "Forms API")
        forms_api_title.grid(column = 0, row = 0)

        visit_forms_xml_button = tkinter.Button(buttons_kit_frame, text = "Visit XML", command = self.forms_api_login.visit_api)
        visit_forms_xml_button.grid(column = 0, row = 1)

        list_forms_button = tkinter.Button(buttons_kit_frame, text = "List Forms", command = self.forms_api_login.list_forms)
        list_forms_button.grid(column = 0, row = 2)

        count_forms_button = tkinter.Button(buttons_kit_frame, text = "Count Forms", command = self.forms_api_login.count_forms)
        count_forms_button.grid(column = 0, row = 3)

        #-----Submissions API Buttons-----#

        submissions_api_title = tkinter.Label(buttons_kit_frame, text = "Submissions API")
        submissions_api_title.grid(column = 1,row = 0)

        submissions_entry = tkinter.Entry(buttons_kit_frame, textvariable = self.submissions_form_id)
        submissions_entry.grid(column = 1, row = 1)

        visit_submissions_xml_button = tkinter.Button(buttons_kit_frame, text = "Visit XML", command = self.gui_visit_submissions_xml)
        visit_submissions_xml_button.grid(column = 1, row = 2)

        tally_responses_button = tkinter.Button(buttons_kit_frame, text = "Tally Responses", command = self.gui_tally_responses)
        tally_responses_button.grid(column = 1, row = 3)

        #-----Images API Buttons-----#
        images_api_title = tkinter.Label(buttons_kit_frame, text = "Images API")
        images_api_title.grid(column = 2, row = 0)

        images_api_entry = tkinter.Entry(buttons_kit_frame, textvariable = self.images_form_id)
        images_api_entry.grid(column = 2, row = 1)

        view_image_button = tkinter.Button(buttons_kit_frame, text = "View Image", command = self.gui_view_image)
        view_image_button.grid(column = 2, row = 2)

        #-----Reference Data API Buttons-----#
        reference_data_api_title = tkinter.Label(buttons_kit_frame, text = "Reference Data API")
        reference_data_api_title.grid(column = 3, row = 0)

        visit_reference_data_api_button = tkinter.Button(buttons_kit_frame, text = 'Visit Reference Data', command = self.ref_api_login.visit_api)
        visit_reference_data_api_button.grid(column = 3, row = 1)


        #-----CSV Meta Data API Buttons-----#
        csv_meta_data_api_title = tkinter.Label(buttons_kit_frame, text = "CSV Meta Data API")
        csv_meta_data_api_title.grid(column = 4, row = 0)

        meta_form_id_entry = tkinter.Entry(buttons_kit_frame, textvariable = self.meta_form_id)
        meta_form_id_entry.grid(column = 4, row = 1)

        visit_meta_api_button = tkinter.Button(buttons_kit_frame, text = 'Visit XML', command = self.gui_visit_meta_xml)
        visit_meta_api_button.grid(column = 4, row = 2)


        #-----CSV API Buttons-----#
        csv_api_title = tkinter.Label(buttons_kit_frame, text = "CSV API")
        csv_api_title.grid(column = 5, row = 0)


        #-----Dispatch Items API Buttons-----#
        dispatch_items_api_title = tkinter.Label(buttons_kit_frame, text = "Dispatch Items API")
        dispatch_items_api_title.grid(column = 6, row = 0)


        #-----Submissions Push Notifications API Buttons-----#
        submissions_push_notifications_api_title = tkinter.Label(buttons_kit_frame, text = "Dispatch Items API")
        submissions_push_notifications_api_title.grid(column = 7, row = 0)
      
    def gui_tally_responses(self):
        submissions_obj = Submissions_API(self.account_info, self.submissions_form_id.get())
        submissions_obj.tally_responses()

    def gui_visit_submissions_xml(self):
        submissions_obj = Submissions_API(self.account_info, self.submissions_form_id.get())
        submissions_obj.visit_api()

    def gui_view_image(self):
        image_obj = Images_API(self.account_info, self.images_form_id.get())
        image_obj.visit_api()

    def gui_visit_meta_xml(self):
        meta_obj = CSV_Meta_Data_API(self.account_info, self.meta_form_id.get())
        meta_obj.visit_api()

    def create_console(self):
        large_console = tkinter.scrolledtext.ScrolledText(self.mainframe)
        large_console.grid(column = 0, row = 8, columnspan = 2)

mainWindow = tkinter.Tk()
SurveyorInterface(mainWindow)
mainWindow.mainloop()
