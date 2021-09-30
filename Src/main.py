import json
from datetime import datetime
import time
import PySimpleGUI as sg
import os

# import all the custom functions
from functionalities import *

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

    sg.ChangeLookAndFeel(settings[5]['theme'])
    sg.SetOptions(element_padding=((4,4),2))
    today_date = datetime.now().strftime(date_format)

    #define layout
    date = datetime.now().strftime(date_format)
    layout1 = [[sg.CalendarButton('Date', target='-DATE-', pad=None, font=('MS Sans Serif', 10, 'bold'), size=(5,1),
                    button_color=('red', 'white'), key='_CURRENT_DATE_', format=(date_format)),sg.In(today_date, key='-DATE-', size=(20,1), enable_events=True)],
            [sg.T('What\'s on your mind?'),sg.Multiline(default_text='',size=(90,6), key='message', do_not_clear=True) ],
            [sg.Button('Show Preview', button_color=('white', 'blue')), sg.Button('Save', button_color=('white', 'springgreen4'))], 
            [sg.Output(key='_output_', size=(90,10), font='Courier 10')]]

    layout2=[[sg.CalendarButton('From', target='-FROM-', pad=None, font=('MS Sans Serif', 10, 'bold'), size=(7,1),
                    button_color=('red', 'white'), key='_START_DATE_', format=(date_format)),sg.In(today_date, key='-FROM-', enable_events=True)],
            [sg.CalendarButton('To', target='-TO-', pad=None, font=('MS Sans Serif', 10, 'bold'), size=(7,1),
                    button_color=('red', 'white'), key='_END_DATE_', format=(date_format)),sg.In(today_date, key='-TO-', enable_events=True)],
            [sg.Button('Show Memoirs', button_color=('white', 'springgreen4'))], 
            [sg.Output(key='_memoirs_', size=(90,15), font='Courier 10')]]

    text_size = (38,1)
    layout3= [[sg.Text('Force save: ', size=text_size), sg.Radio('Enable', 2, enable_events=True, key='TRUE1', default=settings[0]['force_save']), 
                    sg.Radio('Disable', 2, enable_events=True, key='FALSE1', default= not settings[0]['force_save'])],
            [sg.Text('Quit after saving memoiri: ', size=text_size), sg.Radio('Enable', 3, enable_events=True, key='TRUE2', default=settings[1]['quit_after_saving_memoir']), 
                    sg.Radio('Disable', 3, enable_events=True, key='FALSE2', default= not settings[1]['quit_after_saving_memoir'])],
            [sg.Text('Delay (in sec) (when Quit after saving turned to true): ', size=text_size), 
            sg.Slider(range=(1, 10), key="_delay_", default_value=settings[1]['delay'], size=(20,10), orientation='horizontal', font=('Helvetica', 12))],
            [sg.Text('Date format: ', size=text_size), sg.Combo(list(temp_dic.keys()), default_value=settings[3]['date_format'], key="_date_format_")],
            [sg.Text('Tab selected color: ', size=text_size), 
            sg.ColorChooserButton('Color', target='color-text', pad=None, key='-color-', button_color=('white', settings[2]['tab_selected_color'])), sg.In(key='color-text', enable_events=True, visible=False)],
            [sg.Text('Max records to display in preview: ', size=text_size), 
            sg.Slider(range=(10, 100), key="_limit_", default_value=settings[4]['max_records_to_display'], size=(20,10), orientation='horizontal', font=('Helvetica', 12))],
            [sg.Text('Theme: ', size=text_size), sg.Combo(sg.theme_list(), default_value= settings[5]['theme'],key="_theme_"), sg.Button('Themes Preview')],
            [sg.Button('Reset settings'), sg.Button('Save settings')],
            [sg.Text("Status", size=text_size), sg.Output(key='_status_', size=(70, 1), font='Courier 10')]]

    layout4 = [
            [sg.Radio('Delete All', 4, enable_events=True, key='delete-all', default=False), 
            sg.Radio('In a date range', 4, enable_events=True, key='delete-in-range', default=True)],
            [sg.CalendarButton('From', target='-DEL-FROM-', pad=None, font=('MS Sans Serif', 10, 'bold'), size=(7,1),
                    button_color=('red', 'white'), key='del-start-date', format=(date_format)),sg.In(key='-DEL-FROM-', enable_events=True)],
            [sg.CalendarButton('To', target='-DEL-TO-', pad=None, font=('MS Sans Serif', 10, 'bold'), size=(7,1),
                    button_color=('red', 'white'), key='del-end-date', format=(date_format)),sg.In(key='-DEL-TO-', enable_events=True)],
            [sg.Button("Deletion Preview", button_color=('white', 'springgreen4')), sg.Button("Delete Records", button_color=('white', 'firebrick3'))],
            [sg.Output(key='_deletion_status_', size=(90,15), font='Courier 10')]
            ]

    #Define Layout with Tabs         
    tabgrp = [[sg.TabGroup([[sg.Tab('Write', layout1,border_width =10,
                                    element_justification= 'center'),
                        sg.Tab('Read', layout2),
                        sg.Tab('Delete', layout4),
                        sg.Tab('Settings', layout3)                    
                            ]], 
                            tab_location='centertop', selected_background_color=settings[2]['tab_selected_color'],
                            selected_title_color='Red' if settings[2]['tab_selected_color'] == "Yellow" else "White",
                        border_width=5), sg.Button('Close')]]  

    #Define Window
    window =sg.Window("E-Memoir",tabgrp, icon=os.path.join('Src', 'icon.ico'))   

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

            # update the color of the button
        window['-color-'].update(button_color=('white', values['color-text']))
            
    #access all the values and if selected add them to a string
    window.close()        