import json
from datetime import datetime
import time
import PySimpleGUI as sg
import os


def read_settings(reset=False) :
    # reset arg is used when the settings need to be reset
    if reset or not os.path.exists("settings.json") or os.path.getsize("settings.json") == 0:
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
            }
        ]
        with open("settings.json", "w") as f:
            # write the settings to the file
            f.write(json.dumps(settings))
    else :
        settings = json.load(open("settings.json"))

    return settings


def change_date_format(new_format, old_format) :
    # to change the date format in the memoir file
    lst = json.load(open("memoir.json"))
    for i in lst:
        i['date'] = datetime.strptime(i['date'], old_format).strftime(new_format)

    with open("memoir.json", "w") as f :
        f.write(json.dumps(lst))


def save_message_to_file(dic, message, date_format) :
    current_time = datetime.now()
    date, time = current_time.strftime(date_format), current_time.strftime("%H-%M-%S")
        
    dic += [{"date": date, "time": time, "message": message}] 

    with open("memoir.json", "w") as f :
        f.write(json.dumps(dic))


def write_functionality(window, event, values, settings, date_format) :
    date = datetime.now().strftime(date_format)
    msg = values['message']

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
        save_message_to_file(dic, msg, date_format)
        # clear the thing first
        window['_output_'].update("\n\nSaved Successfully")

    elif event == "Show Preview":
        # just show the memoir without saving
        window['_output_'].update(f"Date: {date}\n\nMessage:\n{msg}")


def read_functionality(window, event, values, date_format) :
    start_date, end_date = datetime.strptime(values['-FROM-'], date_format), datetime.strptime(values['-TO-'], date_format)
    string = ""
    # open the json file and loop over all the entries
    for dic in json.load(open("memoir.json")):
        _date = datetime.strptime(dic['date'], date_format)
        if _date >= start_date and _date <= end_date :
            # print the memoir 
            string += f"Date: {dic['date']}" + " "*20 + f"Time: {dic['time']}\n{dic['message']}\n" + "-"*60 + "\n"
    
    window['_memoirs_'].update(string)


def update_settings(window, event, values, settings, temp_dic) :
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
        settings[2]['tab_selected_color'] = values['_tab_selected_color_']
        settings[3]['date_format'] = values['_date_format_']

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
        window['_tab_selected_color_'].update('Blue')
        window['_date_format_'].update('28-November-1999')

        # reset the settings file as well
        read_settings(reset=True)
        window['_status_'].update("Settings reset successfully. Restart the app to see the effects.")


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
    # need the proper date format 
    temp_dic = {"28-11-1999": "%d-%m-%Y", "28-Nov-1999": "%d-%b-%Y", "28-November-1999": "%d-%B-%Y", 
            "11-28-1999": "%m-%d-%Y", "Nov-28-1999": "%b-%d-%Y", "November-28-1999": "%B-%d-%Y",
            "1999-11-28": "%Y-%m-%d", "1999-Nov-28": "%Y-%b-%d", "1999-November-28": "%Y-%B-%d"}
    # replace the date format
    date_format = temp_dic[settings[3]['date_format']]
    colors = ['Blue', 'Red', 'Yellow', 'Orange', 'Pink', 'Green', 'Violet']

    sg.ChangeLookAndFeel('Dark')
    sg.SetOptions(element_padding=((4,4),2))
    #define layout
    date = datetime.now().strftime(date_format)
    layout1 = [[sg.Text(f'Date: {date}', size=(20,1))],
            [sg.T('What\'s on your mind?'),sg.Multiline(default_text='',size=(90,6), key='message', do_not_clear=True) ],
            [sg.Button('Show Preview'), sg.Button('Save')], 
            [sg.T('Preview')],
            [sg.Output(key='_output_', size=(90,10), font='Courier 10')]]

    layout2=[[sg.CalendarButton('From', target='-FROM-', pad=None, font=('MS Sans Serif', 10, 'bold'), size=(7,1),
                    button_color=('red', 'white'), key='_START_DATE_', format=(date_format)),sg.In(key='-FROM-', enable_events=True)],
            [sg.CalendarButton('To', target='-TO-', pad=None, font=('MS Sans Serif', 10, 'bold'), size=(7,1),
                    button_color=('red', 'white'), key='_END_DATE_', format=(date_format)),sg.In(key='-TO-', enable_events=True)],
            [sg.Button('Show Memoirs')], 
            [sg.Output(key='_memoirs_', size=(90,15), font='Courier 10')]]

    text_size = (38,1)
    layout3= [[sg.Text('Force save: ', size=text_size), sg.Radio('True', 2, enable_events=True, key='TRUE1', default=settings[0]['force_save']), 
                    sg.Radio('False', 2, enable_events=True, key='FALSE1', default= not settings[0]['force_save'])],
            [sg.Text('Quit after saving memoiri: ', size=text_size), sg.Radio('True', 3, enable_events=True, key='TRUE2', default=settings[1]['quit_after_saving_memoir']), 
                    sg.Radio('False', 3, enable_events=True, key='FALSE2', default= not settings[1]['quit_after_saving_memoir'])],
            [sg.Text('Delay (in sec) (when Quit after saving turned to true): ', size=text_size), 
            sg.Slider(range=(1, 10), key="_delay_", default_value=settings[1]['delay'], size=(20,10), orientation='horizontal', font=('Helvetica', 12))],
            [sg.Text('Date format: ', size=text_size), sg.Combo(list(temp_dic.keys()), default_value=settings[3]['date_format'], key="_date_format_")],
            [sg.Text('Tab selected color: ', size=text_size), sg.Combo(colors, default_value= settings[2]['tab_selected_color'],key="_tab_selected_color_")],
            [sg.Button('Reset settings'), sg.Button('Save settings')],
            [sg.Text("Status", size=text_size), sg.Output(key='_status_', size=(70, 1), font='Courier 10')]]

    #Define Layout with Tabs         
    tabgrp = [[sg.TabGroup([[sg.Tab('Write', layout1,border_width =10,
                                    element_justification= 'center'),
                        sg.Tab('Read', layout2),
                        sg.Tab('Settings', layout3)
                            ]], 
                            tab_location='centertop', selected_background_color=settings[2]['tab_selected_color'],
                            selected_title_color='Red' if settings[2]['tab_selected_color'] == "Yellow" else "White",
                        border_width=5), sg.Button('Close')]]  

    #Define Window
    window =sg.Window("E-Memoir",tabgrp)   

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
                read_functionality(window, event, values, date_format)
            
            else :
                window['_memoirs_'].update('Please select the From and To dates.......')
        
        if event in ("Save settings", "Reset settings") :
            update_settings(window, event, values, settings, temp_dic)
            
    # close the window
    window.close()    