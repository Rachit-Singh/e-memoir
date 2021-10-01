import json
from datetime import datetime
import time
import PySimpleGUI as sg
import os
import keyring # for password storage
import hashlib
import platform

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# WINDOWS
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

## LOGIN SCREEN THAT ASKS FOR PASSWORD 
def loginWindow_fn(theme, password, settings) :
    sg.change_look_and_feel(theme)

    layout= [
                [sg.Image(settings[6]['image_path'])],
                [sg.Text("Password", size=(10,1))],
                [sg.Input(password_char='*', key='-PASSWORD-', size=(30,1)), sg.Text('X', key='-wrongPassword-', text_color='Red', visible=False)],
                [sg.Button('Login', button_color=('White', 'springgreen4')), sg.Button('Exit', button_color=('White', 'firebrick3'))]
            ]
    window3 = sg.Window('Login', layout, element_justification='c',
                    resizable=True, icon=settings[6]['icon_path']) #make window resizable
    
    passed = False
    while True :
        event, values = window3.read()
        if event in (sg.WIN_CLOSED, "Exit") :
            break

        if event == 'Login' :
            hashed_password = hashlib.sha256(values['-PASSWORD-'].encode()).hexdigest() # hashing the password
            if hashed_password == password :
                passed = True
                break
            else :
                window3['-wrongPassword-'].update(visible=True)

    window3.close()
    return passed

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

## MAIN WINDOW LAYOUT FORMAT
def mainWindowLayout_fn(date_format, settings, temp_dic, have_password=False) :
        today_date = datetime.now().strftime(date_format)

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

        password_settings = [sg.Text('Password: ', size=text_size), 
        sg.Button('Change Password') if have_password else sg.Button('Set Password')] + ([sg.Button('Remove Password')] if have_password else []) 

        layout3= [[sg.Text('Force save: ', size=text_size), sg.Radio('Enable', 2, enable_events=True, key='TRUE1', default=settings[0]['force_save']), 
                        sg.Radio('Disable', 2, enable_events=True, key='FALSE1', default= not settings[0]['force_save'])],
                [sg.Text('Quit after saving memoir: ', size=text_size), sg.Radio('Enable', 3, enable_events=True, key='TRUE2', default=settings[1]['quit_after_saving_memoir']), 
                        sg.Radio('Disable', 3, enable_events=True, key='FALSE2', default= not settings[1]['quit_after_saving_memoir'])],
                [sg.Text('Delay (in sec) (when Quit after saving is enabled): ', size=text_size), 
                sg.Slider(range=(1, 10), key="_delay_", default_value=settings[1]['delay'], size=(20,10), orientation='horizontal', font=('Helvetica', 12))],
                [sg.Text('Date format: ', size=text_size), sg.Combo(list(temp_dic.keys()), default_value=settings[3]['date_format'], key="_date_format_")],
                [sg.Text('Tab selected color: ', size=text_size), 
                sg.ColorChooserButton('Color', target='color-text', pad=None, key='-color-', button_color=('white', settings[2]['tab_selected_color'])), sg.In(key='color-text', enable_events=True, visible=False)],
                [sg.Text('Max records to display in preview: ', size=text_size), 
                sg.Slider(range=(10, 100), key="_limit_", default_value=settings[4]['max_records_to_display'], size=(20,10), orientation='horizontal', font=('Helvetica', 12))],
                [sg.Text('Theme: ', size=text_size), sg.Combo(sg.theme_list(), default_value= settings[5]['theme'],key="_theme_"), sg.Button('Themes Preview')],
                
                password_settings,
                
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

        return tabgrp

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

## CHANGE PASSWORD WINDOW
def change_password_fn(theme, settings) :
    password = keyring.get_password('e-memoir', 'user')
    sg.change_look_and_feel(theme)

    layout= [
                [sg.Text("Old Password", size=(25,1)), sg.Input(password_char='*', key='-OLD-PASSWORD-', size=(25,1)), sg.Text('X', key='-wrong-', text_color='Red', visible=False)],
                [sg.Text("New Password", size=(25,1)), sg.Input(password_char='*', key='-NEW-PASSWORD-', size=(25,1)), sg.Text('NO VALUE', key='-noValue1-', text_color='Red', visible=False)],
                [sg.Text("Confirm Password", size=(25,1)), sg.Input(password_char='*', key='-CONFIRM-PASSWORD-', size=(25,1)), sg.Text('MISMATCH', key='-mismatch-', text_color='Red', visible=False), sg.Text('NO VALUE', key='-noValue2-', text_color='Red', visible=False)],
                [sg.Button('Change', button_color=('White', 'springgreen4')), sg.Button('Cancel', button_color=('White', 'firebrick3'))]
            ]
    window3 = sg.Window('Change Password', layout, element_justification='c',
                    resizable=True, icon=settings[6]['icon_path']) #make window resizable
    
    passed = False
    while True :
        event, values = window3.read()
        if event in (sg.WIN_CLOSED, "Cancel") :
            break
        
        # setting visibility off
        window3['-mismatch-'].update(visible=False)
        window3['-wrong-'].update(visible=False)
        window3['-noValue1-'].update(visible=False)
        window3['-noValue2-'].update(visible=False)

        if event == 'Change' :
            # check if there are values provided in the textboxes
            if not values['-OLD-PASSWORD-'] :
                window3['-wrong-'].update(visible=True)
            elif not values['-NEW-PASSWORD-'] :
                window3['-noValue1-'].update(visible=True)
            elif not values['-CONFIRM-PASSWORD-'] :
                window3['-noValue2-'].update(visible=True)
            else :
                # check if the old password is correct or not
                hashed_password = hashlib.sha256(values['-OLD-PASSWORD-'].encode()).hexdigest() # hashing the password
                if hashed_password == password :
                    # check if both the password match
                    if values['-NEW-PASSWORD-'] == values['-CONFIRM-PASSWORD-'] :
                        # delete the old password
                        keyring.delete_password('e-memoir', 'user')
                        # create the new password
                        keyring.set_password('e-memoir', 'user', hashlib.sha256(values['-NEW-PASSWORD-'].encode()).hexdigest())
                        passed = True
                        break
                    else :
                        # both the passwords donot match
                        window3['-mismatch-'].update(visible=True)
                else :
                    # entered old password is wrong
                    window3['-wrong-'].update(visible=True)

    window3.close()
    return passed

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

## REMOVE PASSWORD WINDOW
def remove_password_fn(theme, settings) :
    password = keyring.get_password('e-memoir', 'user')
    sg.change_look_and_feel(theme)

    layout= [   
                [sg.Text("Password", size=(25,1)), sg.Input(password_char='*', key='-PWD-', size=(25,1)), sg.Text('X', key='-wrongPwd-', text_color='Red', visible=False)],
                [sg.Button('Remove', button_color=('White', 'springgreen4')), sg.Button('Cancel', button_color=('White', 'firebrick3'))],
                [sg.Text("App will close after removing the password", text_color='Red', key='-text-')]
            ]

    window3 = sg.Window('Remove Password', layout, element_justification='c',
                    resizable=True, icon=settings[6]['icon_path']) #make window resizable

    passed = False
    while True :
        event, values = window3.read()

        if event in (sg.WIN_CLOSED, "Cancel") :
            break

        if event == "Remove" :
            if not values['-PWD-'] :
                window3['-wrongPwd-'].update(visible=True)
            # check if the password is correct or not
            elif hashlib.sha256(values['-PWD-'].encode()).hexdigest() == password :
                keyring.delete_password('e-memoir', 'user')
                passed = True
                window3['-text-'].update('Password removed successfully')
                time.sleep(int(settings[1]['delay']))
                break
            else :
                window3['-wrongPwd-'].update(visible=True)

    window3.close()
    return passed

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

## SET PASSWORD WINDOW
def set_password_fn(theme, settings) :
    sg.change_look_and_feel(theme)

    layout= [   
                [sg.Text("Password", size=(25,1)), sg.Input(password_char='*', key='-NEW-PWD-', size=(25,1)), sg.Text('NO VALUE', key='-noVal1-', text_color='Red', visible=False)],
                [sg.Text("Confirm Password", size=(25,1)), sg.Input(password_char='*', key='-CONFIRM-PWD-', size=(25,1)), sg.Text('MISMATCH', key='-mismatched-', text_color='Red', visible=False), sg.Text('NO VALUE', key='-noVal2-', text_color='Red', visible=False)],
                [sg.Button('Set', button_color=('White', 'springgreen4')), sg.Button('Cancel', button_color=('White', 'firebrick3'))]
            ]

    window3 = sg.Window('Set Password', layout, element_justification='c',
                    resizable=True, icon=settings[6]['icon_path']) #make window resizable

    passed = False
    while True :
        event, values = window3.read()
        if event in (sg.WIN_CLOSED, "Cancel") :
            break
        
        # setting visibility off
        window3['-mismatched-'].update(visible=False)
        window3['-noVal1-'].update(visible=False)
        window3['-noVal2-'].update(visible=False)

        if event == "Set" :
            # check if there are values provided in the textboxes
            if not values['-NEW-PWD-'] :
                window3['-noVal1-'].update(visible=True)
            elif not values['-CONFIRM-PWD-'] :
                window3['-noVal2-'].update(visible=True)
            else :
                # if both match
                if values['-NEW-PWD-'] == values['-CONFIRM-PWD-'] :
                    # set the password
                    keyring.set_password('e-memoir', 'user', hashlib.sha256(values['-NEW-PWD-'].encode()).hexdigest())
                    passed = True
                    break
                else :
                    window3['-mismatched-'].update(visible=True)
    
    window3.close()
    return passed

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~