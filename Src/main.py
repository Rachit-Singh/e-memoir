import json
from datetime import datetime
import time
import PySimpleGUI as sg
import os
import keyring # for password storage
import hashlib

# import all the custom functions
from functionalities import *

# import all the window formats
from windows import *

if __name__ == "__main__" :
    # check if the memoir file exists
    # OR
    # if the memoir file is deliberately deleted, create an empty list to store future data
    if not os.path.exists("memoir.json") or os.path.getsize("memoir.json") == 0:
            # if is does not exists, create a new one
            with open("memoir.json", "w") as f :
                    f.write(json.dumps([]))

    # read the settings file
    settings = read_settings()

    # check if there is any password set or not
    password = keyring.get_password('e-memoir', 'user')

    # if there is a password, run the login screen and get if the password was correct or not
    # if there is no password, just input True in run_app variable
    theme = settings[5]['theme']
    run_app = loginWindow_fn(theme, password, settings) if password else True

    # run the app only if the password was right or there was no password at all
    if run_app :
        # need the proper date format 
        temp_dic = {"28-11-1999": "%d-%m-%Y", "28-Nov-1999": "%d-%b-%Y", "28-November-1999": "%d-%B-%Y", 
                "11-28-1999": "%m-%d-%Y", "Nov-28-1999": "%b-%d-%Y", "November-28-1999": "%B-%d-%Y",
                "1999-11-28": "%Y-%m-%d", "1999-Nov-28": "%Y-%b-%d", "1999-November-28": "%Y-%B-%d"}
        # replace the date format
        date_format = temp_dic[settings[3]['date_format']]
        colors = ['Blue', 'Red', 'Yellow', 'Orange', 'Pink', 'Green', 'Violet']

        sg.ChangeLookAndFeel(theme)
        sg.SetOptions(element_padding=((4,4),2))

        tabgrp = mainWindowLayout_fn(date_format, settings, temp_dic, have_password=True if password else False)
        #Define Window
        window =sg.Window("E-Memoir",tabgrp, icon=os.path.join(os.path.dirname(__file__), 'icon.ico'))   

        while True:             # Event Loop
            event, values = window.Read()      
            if event in (None, "Close") :
                break
            
            if values['message'] :
                write_functionality(window, event, values, settings, date_format)

            # if no message is entered and then also the save or preview button is clicked
            elif event in ("Save", "Show Preview") :
                window['_output_'].update("No message entered.....")
                
            # if quit after saving memoir is enabled, quit the program after a specified delay
            if event == 'Save' and settings[1]['quit_after_saving_memoir'] :
                window['_output_'].update('Memoir saved. Quiting.. See you tomorrow :)')
                time.sleep(settings[1]['delay'])
                break
            
            # if the show memoirs button is clicked
            if event == "Show Memoirs" :
                # if the dates are entered
                if values['-FROM-'] and values['-TO-'] :
                    read_functionality(window, values, date_format, int(settings[4]["max_records_to_display"]))
                
                else :
                    window['_memoirs_'].update('Please select the From and To dates.......')
            
            if event in ("Save settings", "Reset settings") :
                update_settings(window, event, values, settings, temp_dic)

            if event in ("Deletion Preview", "Delete Records") :
                delete_functionality(window, event, values, date_format, int(settings[4]["max_records_to_display"]), delete_all=values['delete-all'])

            if event == "Themes Preview" :
                # open a window with the theme preview
                themes_preview_fn()

            if event == "Change Password" :
                # open the change password window
                if change_password_fn(theme, settings) :
                    window['_status_'].update('Password changed successfully')

            if event == "Remove Password" :
                # open the remove password window
                if remove_password_fn(theme, settings) :
                    break
            
            # since we are not refreshing the layout after setting password
            # it may happen that user clicks on it again and sets a new password again
            # which should not happen (that is the function of Change Password)
            if event == "Set Password" :
                if keyring.get_password('e-memoir', 'user'):
                    # the password has already been set
                    window['_status_'].update('Password has already been set.')
                elif set_password_fn(theme, settings):
                    # open the set password window, set the password and show the message
                    window['_status_'].update("Password set successfully.")

            # update the color of the button
            window['-color-'].update(button_color=('white', values['color-text']))
                
        #access all the values and if selected add them to a string
        window.close()    