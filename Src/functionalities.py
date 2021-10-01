import json
from datetime import datetime
import time
import PySimpleGUI as sg
import os
import platform
import getpass

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
### FUNCTIONALITIES
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

## READ AND WRITE SETTINGS 
def read_settings(reset=False) :
    # reset arg is used when the settings need to be reset
    if reset or not os.path.exists("settings.json") or os.path.getsize("settings.json") == 0:
        # searching the C:\Users\{username} directory in Windows and /home/{username} directory in Linux
        # for the path of icon ico and png file
        image_path, theme_path, icon_path = 'Diary-icon.png', 'themes.ico', 'icon.ico'
        username = getpass.getuser()
        paths = os.path.join(r"C:\Users",username) if platform.system()=="Windows" else os.path.join("/home",username)
        for root, _, files in os.walk(paths):
            for name in files :
                if name == 'Diary-icon.png' :
                    image_path = os.path.abspath(os.path.join(root, name))
                elif name == 'icon.ico' :
                    icon_path = os.path.abspath(os.path.join(root, name))
                elif name == 'themes.ico' :
                    theme_path = os.path.abspath(os.path.join(root, name))

        settings = [
            {
                "force_save" : False,
                "_comment_" : "Set this true will save the same memoir being pushed the same day again"
            },
            {
                "quit_after_saving_memoir" : False,
                "delay" : 2,
                "_comment_" : "Will exit the program after the memoir is saved successfully after a fixed delay"
            },
            {
                "tab_selected_color" : "Blue",
                "_comment_" : "Color of the tab when it is selected"
            },
            {
                "date_format" : "28-November-1999",
                "_comment" : "format of the date to be used in the memoir"
            },
            {
                "max_records_to_display" : 20,
                "_comment_" : "max number of records to be displayed in preview"
            },
            {
                "theme" : "Dark",
                "_comment_" : "theme of the GUI"
            },
            {
                "icon_path" : icon_path,
                "theme_path" : theme_path,
                "image_path" : image_path
            }
        ]
        with open("settings.json", "w") as f:
            # write the settings to the file
            f.write(json.dumps(settings))
    else :
        settings = json.load(open("settings.json"))

    return settings

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

## CHANGE THE DATE FORMAT IN THE MEMOIR FILE
def change_date_format(new_format, old_format) :
    # to change the date format in the memoir file
    lst = json.load(open("memoir.json"))
    for i in lst:
        i['date'] = datetime.strptime(i['date'], old_format).strftime(new_format)

    with open("memoir.json", "w") as f :
        f.write(json.dumps(lst))

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

## SAVE THE MEMOIR TO THE FILE
def save_message_to_file(dic, message, date, date_format) :
    current_time = datetime.now()
    cur_date = current_time.strftime(date_format)
    cur_time = current_time.strftime("%H-%M-%S") if cur_date == date else f"Written on {cur_date}"

    dic += [{"date": date, "time": cur_time, "message": message}] 
    with open("memoir.json", "w") as f :
            f.write(json.dumps(dic))

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

## HANDLES THE COMPLETE WRITE TAB IN THE APP
def write_functionality(window, event, values, settings, date_format) :
    date, msg = values['-DATE-'], values['message']

    # load the list in the file beforehand
    dic = json.load(open("memoir.json"))

    # check if the same message is being pushed again
    # if the force_save is enabled, skip this
    if msg+date in [i['message']+i['date'] for i in dic] and not settings[0]['force_save']:
        window['_output_'].update("Memoir already saved...")
        return

    # if the save button is clicked
    if event == "Save" :
        # save the memoir
        save_message_to_file(dic, msg, date, date_format)
        # clear the thing first
        window['_output_'].update("\n\nSaved Successfully")

    elif event == "Show Preview":
        # just show the memoir without saving
        window['_output_'].update(f"Date: {date}\n\nMessage:\n{msg}")

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

## HANDLES THE COMPLETE READ TAB IN THE APP
def read_functionality(window, values, date_format, limit) :
    start_date, end_date = datetime.strptime(values['-FROM-'], date_format), datetime.strptime(values['-TO-'], date_format)

    lst = []
    # open the json file and loop over all the entries
    for dic in json.load(open("memoir.json")):
        _date = datetime.strptime(dic['date'], date_format)
        if _date >= start_date and _date <= end_date :
            lst.append(f"Date: {dic['date']}" + " "*20 + f"Time: {dic['time']}\n{dic['message']}\n" + "-"*60)
    
    string = f"{len(lst)} records found. " + ((f"{len(lst)-limit} records truncated\n\n" if len(lst) > limit else "\n\n")) 
    string += "\n".join(lst)
    window['_memoirs_'].update(string)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

## HANDLES THE COMPLETE DELETE TAB IN THE APP
def delete_functionality(window, event, values, date_format, limit, delete_all=False) :
    records = json.load(open("memoir.json"))

    if delete_all :
        if event == "Deletion Preview" :
            # display at max only {limit} records in the output area
            string = f"{len(records)} records found." + (f"{len(records)-limit} records truncated\n\n" if len(records) > limit else "\n\n")
            for i in records[:limit] :
                string += f"Date: {i['date']}" + " "*20 + f"Time: {i['time']}\n{i['message']}\n" + "-"*60 + "\n"
            window['_deletion_status_'].update(string)
        
        elif event == "Delete Records" :
            if len(records) > 0:
                # will not work if there are no records in the file
                response = sg.popup_ok_cancel(f"{len(records)} records found. Are you sure you want to delete them? It will not be possible to retrieve them.", title='Confirm deletion')
                if response == 'OK' :
                    # delete all the records
                    with open("memoir.json", "w") as f:
                        f.write(json.dumps([]))
                    window['_deletion_status_'].update(f"All records deleted successfully.")

                else :
                    window['_deletion_status_'].update("Deletion terminated successfully. No records deleted")
            
            else :
                sg.popup("No records found.")

    else :
        # delete all the records in a date range
        start_date, end_date = datetime.strptime(values['-DEL-FROM-'], date_format), datetime.strptime(values['-DEL-TO-'], date_format)

        records_to_be_deleted = []
        for record in records :
            _date = datetime.strptime(record['date'], date_format)
            # if the date falls between the provided dates
            if _date >= start_date and _date <= end_date :
                records_to_be_deleted.append(record)

        if event == "Deletion Preview" :
            # display at max only {limit} records in the output area
            string = f"{len(records_to_be_deleted)} records found." + (f"{len(records_to_be_deleted)-limit} records truncated\n\n" if len(records_to_be_deleted) > limit else "\n\n")
            for i in records_to_be_deleted[:limit] :
                string += f"Date: {i['date']}" + " "*20 + f"Time: {i['time']}\n{i['message']}\n" + "-"*60 + "\n"
            window['_deletion_status_'].update(string)
            
        elif event == "Delete Records" :
            if len(records_to_be_deleted) > 0 :
                response = sg.popup_ok_cancel(f"{len(records_to_be_deleted)} records found. Are you sure you want to delete them? It will not be possible to retrieve them.", title='Confirm deletion')
                if response == 'OK' :
                    # delete all of them
                    for i in records_to_be_deleted :
                        records.remove(i)
                    # write them back to the file
                    with open("memoir.json", "w") as f:
                        f.write(json.dumps(records))
                    window['_deletion_status_'].update(f"{len(records_to_be_deleted)} records deleted successfully.")

                else :
                    # terminate the deletion
                    window['_deletion_status_'].update("Deletion terminated successfully. No records deleted")
            
            else :
                _ = sg.popup("No records found.")

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

## HANDLES THE COMPLETE SETTINGS TAB IN THE APP
def update_settings(window, event, values, settings, temp_dic) :
    date_format = temp_dic[settings[3]['date_format']]
    if event == 'Save settings' :
        if values['_date_format_'] != settings[3]['date_format'] :
            # this means the date format has been changed
            # change the date format in the memoir file
            # the date_format variable still holds the old date_format as it reads the format from the file and file has 
            # only been read at the start once 
            change_date_format(new_format=temp_dic[values['_date_format_']], old_format=date_format)

        settings[0]['force_save'] = values['TRUE1']
        settings[1]['quit_after_saving_memoir'] = values['TRUE2']
        settings[1]['delay'] = int(values['_delay_'])
        settings[2]['tab_selected_color'] = values['color-text']
        settings[3]['date_format'] = values['_date_format_']
        settings[4]["max_records_to_display"] = values['_limit_']
        settings[5]['theme'] = values['_theme_']

        # overwriting the settings file
        with open("settings.json", "w") as f:
            f.write(json.dumps(settings))
        window['_status_'].update("Settings saved successfully. Restart the app to see the effects.")
        
    if event == "Reset settings" :
        # if the date format is not the dafault one
        if settings[3]['date_format'] != '28-November-1999' :
            change_date_format(new_format='%d-%B-%Y', old_format=date_format)
            
        # have to reset the settings
        window['FALSE1'].update(value=True)
        window['FALSE2'].update(value=True)
        window['_delay_'].update(2)
        window['-color-'].update(button_color=('White', 'Blue'))
        window['_date_format_'].update('28-November-1999')
        window['_limit_'].update(20)
        window['_theme_'].update('Dark')

        # reset the settings file as well
        read_settings(reset=True)
        window['_status_'].update("Settings reset successfully. Restart the app to see the effects.")

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

