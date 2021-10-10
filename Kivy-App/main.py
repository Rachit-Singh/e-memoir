from hashlib import sha256
import re

from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivymd.uix import button
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.core.window import Window
from kivy.base import EventLoop

from kivymd.app import MDApp
from kivy.lang import Builder
from kivymd.uix.button import MDFlatButton, MDRectangleFlatButton, MDRaisedButton
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.picker import MDDatePicker, MDThemePicker
from datetime import datetime
from kivymd.uix.menu import MDDropdownMenu
from kivy.storage.jsonstore import JsonStore
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import TwoLineIconListItem, IconLeftWidget
from kivymd.toast import toast

# Window.size = (360, 600)
Window.softinput_mode = 'pan'
todays_date = datetime.now()

class SetPasswordDialogBox(MDBoxLayout) :
    pass

class RemovePasswordDialogBox(MDBoxLayout) :
    pass

class ChangePasswordDialogBox(MDBoxLayout) :
    pass


class EMemoirApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.screen = Builder.load_file("main.kv")
        menu_items = [
            {
                "text": "ALL",
                "viewclass": "OneLineListItem",
                "on_release": lambda x=f"DELETE ALL": self.menu_callback(x),
            },
            {
                "text": "DATE RANGE",
                "viewclass": "OneLineListItem",
                "on_release": lambda x=f"DATE RANGE": self.menu_callback(x),
            }
        ]
        self.menu = MDDropdownMenu(
            caller=self.screen.ids.deletion_option,
            items=menu_items,
            width_mult=10,
        )

    def build(self):
        self.icon = "Diary-icon.png"
        return self.screen

    def on_stop(self) :
        # save the theme in the memoir-credentials file
        store = JsonStore("memoir-credentials.json")
        store.put("theme", primary_palette=self.theme_cls.primary_palette,
        accent_palette= self.theme_cls.accent_palette, theme_style=self.theme_cls.theme_style)

    def on_start(self):
        EventLoop.window.bind(on_keyboard=self.hook_keyboard)

        # set the theme if available
        try :
            store = JsonStore("memoir-credentials.json")
            self.theme_cls.primary_palette = store.get("theme")["primary_palette"]
            self.theme_cls.accent_palette = store.get("theme")["accent_palette"]
            self.theme_cls.theme_style = store.get("theme")["theme_style"]
        except :
            pass

        # remove the login screen if password is not there
        try :
            # if the key exists, password is set
            _ = JsonStore("memoir-credentials.json").get("pwd")
            password_present = True 
        except :
            password_present = False

        if not password_present :
            self.root.ids.screen_manager.remove_widget(
                self.root.ids.screen_manager.children[0]
            )
            if datetime.now().hour < 12 :
                toast("Good Morning")
            elif datetime.now().hour > 12 and datetime.now().hour < 4 :
                toast("Good Afternoon")
            else :
                toast("Good Evening")

        self.root.ids.date_button.text = todays_date.strftime("%d-%m-%Y")
        self.root.ids.from_date_read.text = f'FROM:  {todays_date.strftime("%d-%m-%Y")}'
        self.root.ids.to_date_read.text = f'TO:  {todays_date.strftime("%d-%m-%Y")}'
        self.root.ids.from_date_delete.text = f'FROM:  {todays_date.strftime("%d-%m-%Y")}'
        self.root.ids.to_date_delete.text = f'TO:  {todays_date.strftime("%d-%m-%Y")}'

        # create the password buttons dynamically
        self.create_password_buttons(password_present)

    def hook_keyboard(self, window, key, *largs):
        # CHECK IF THE BACK BUTTON IS PRESSED AND IF YES, RETURN TO THE PREVIOUS SCREEN
        cur_screen = self.root.ids.screen_manager.current
        if key == 27:
            if cur_screen == "long_memoir_reading_screen" :
                self.screen_change("reading_preview_screen")
            elif cur_screen == "reading_preview_screen" :
                self.screen_change("read_screen")
            elif cur_screen == "deletion_preview_screen" :
                self.screen_change("delete_screen")
            else :
                self.confirm_exit()
            # do what you want, return True for stopping the propagation
            return True 
            
    def nothing(self) :
        # does nothing
        pass
    
    def confirm_exit(self):
        # asks for confirmation
        self.dialog = MDDialog(title="Exit?", 
        buttons=[MDRaisedButton(text="EXIT", on_release=self.stop, md_bg_color=(1, 0.2, 0.2, 1)),
        MDRaisedButton(text="Cancel", on_release=self.close_dialogBox)])
        self.dialog.open()
        return True

    def menu_callback(self, text_item):
        self.root.ids.deletion_option.text = f"CRITERIA: {text_item}"
        self.menu.dismiss()

    def screen_change(self, screen):
        if screen == "read_screen" :
            # make the keyword textField blank
            self.root.ids.search_keyword.text = ""
        # to change screens
        self.root.ids.screen_manager.current = screen

    def credential_check(self) :
        password = self.root.ids.password_textField.text
        if sha256(password.encode()).hexdigest() == JsonStore("memoir-credentials.json").get("pwd")["value"] :
            # password matched
            self.root.ids.screen_manager.current = "write_screen"
            # print a Welcome toast
            if datetime.now().hour < 12 :
                toast("Good Morning")
            elif datetime.now().hour > 12 and datetime.now().hour < 4 :
                toast("Good Afternoon")
            else :
                toast("Good Evening")
        else:
            dialog = MDDialog(title="Incorrect", text="Try again", md_bg_color=(1, 0.2, 0.2, 1))
            dialog.open()

    def set_password_dialog_box(self, obj) :
        self.dialog = MDDialog(
                title="Set Password",
                type="custom",
                content_cls=SetPasswordDialogBox(),
                buttons=[
                    MDFlatButton(
                        text="CANCEL", text_color=self.theme_cls.primary_color,
                        on_release=self.close_dialogBox
                    ),
                    MDRaisedButton(
                        text="SET", 
                        on_release= self.set_password
                    ),
                ],
            )
        self.dialog.open()

    def set_password(self, obj) :
        first, second = self.dialog.content_cls.ids.first_password.text, self.dialog.content_cls.ids.confirm_password.text
        if first == second :
            # save the password
            JsonStore("memoir-credentials.json").put("pwd", value=sha256(first.encode()).hexdigest())
            self.dialog.dismiss()

            # create the other 2 buttons
            self.create_password_buttons(password_present=True)
            toast("Password Saved")
        else:
            MDDialog(title="Password mismatch", md_bg_color=(1, 0.2, 0.2, 1)).open()

    def remove_password_dialog_box(self, obj) :
        self.dialog = MDDialog(
                title="Remove Password",
                type="custom",
                content_cls=RemovePasswordDialogBox(),
                buttons=[
                    MDFlatButton(
                        text="CANCEL", text_color=self.theme_cls.primary_color,
                        on_release=self.close_dialogBox
                    ),
                    MDRaisedButton(
                        text="REMOVE", 
                        on_release= self.remove_password
                    )
                ],
            )
        self.dialog.open()

    def remove_password(self, obj) :
        store = JsonStore("memoir-credentials.json")
        pass_entered = self.dialog.content_cls.ids.remove_current_password.text
        if sha256(pass_entered.encode()).hexdigest() == store.get("pwd")["value"] :
            # remove the password
            store.delete("pwd")
            self.dialog.dismiss()
            # delete the 2 buttons and create the SET password button
            self.create_password_buttons(password_present=False)

            toast("Password Removed")
        else :
            MDDialog(title="Incorrect Password", md_bg_color=(1, 0.2, 0.2, 1)).open()

    def change_password_dialog_box(self, obj) :
        self.dialog = MDDialog(
                title="Change Password",
                type="custom",
                content_cls=ChangePasswordDialogBox(),
                buttons=[
                    MDFlatButton(
                        text="CANCEL", text_color=self.theme_cls.primary_color,
                        on_release=self.close_dialogBox
                    ),
                    MDRaisedButton(
                        text="CHANGE", 
                        on_release= self.change_password
                    ),
                ],
            )
        self.dialog.open()

    def change_password(self, obj) :
        store = JsonStore("memoir-credentials.json")
        pass_entered = self.dialog.content_cls.ids.old_password.text
        new_pwd, confirm_pwd = self.dialog.content_cls.ids.new_password.text, self.dialog.content_cls.ids.confirm_new_password.text

        if sha256(pass_entered.encode()).hexdigest() == store.get("pwd")["value"] :
            if new_pwd == confirm_pwd :
                # remove the password
                store.put("pwd", value=sha256(new_pwd.encode()).hexdigest())
                self.dialog.dismiss()

                toast("Password Changed")
            else :
                MDDialog(title="Password Mismatch", md_bg_color=(1, 0.2, 0.2, 1)).open()
        else :
            MDDialog(title="Incorrect Password", md_bg_color=(1, 0.2, 0.2, 1)).open()

    
    def create_password_buttons(self, password_present) :
        # to create password buttons in the settings screen
        self.root.ids.password_btns_layout.clear_widgets()

        if password_present :
            self.root.ids.password_btns_layout.orientation = "horizontal"
            self.root.ids.password_btns_layout.add_widget(
                MDRectangleFlatButton(text="Change Password",
                pos_hint={"center_x":0.5, "center_y":0.5},
                on_release= self.change_password_dialog_box
                )
            )
            self.root.ids.password_btns_layout.add_widget(
                MDRectangleFlatButton(text="Remove Password",
                pos_hint={"center_x":0.5, "center_y":0.5},
                on_release= self.remove_password_dialog_box
                )
            )
        else :
            self.root.ids.password_btns_layout.orientation = "vertical"
            self.root.ids.password_btns_layout.add_widget(
                MDRectangleFlatButton(text="Set Password", 
                pos_hint={"center_x":0.5, "center_y":0.5}, on_release= self.set_password_dialog_box
                )
            )

    def date_chosen(self, instance, value, id) :
        if id == "date_button" :
            self.root.ids.date_button.text = datetime.strptime(str(value), "%Y-%m-%d").strftime("%d-%m-%Y")
        elif id == "from_date_read":
            self.root.ids.from_date_read.text = f'FROM:  {datetime.strptime(str(value), "%Y-%m-%d").strftime("%d-%m-%Y")}'
        elif id == "to_date_read" :
            self.root.ids.to_date_read.text = f'TO:  {datetime.strptime(str(value), "%Y-%m-%d").strftime("%d-%m-%Y")}'
        elif id == "from_date_delete" :
            self.root.ids.from_date_delete.text = f'FROM:  {datetime.strptime(str(value), "%Y-%m-%d").strftime("%d-%m-%Y")}'
        elif id == "to_date_delete" :
            self.root.ids.to_date_delete.text = f'TO:  {datetime.strptime(str(value), "%Y-%m-%d").strftime("%d-%m-%Y")}'

    def show_date_picker(self, btn_id) :
        date_dialog= MDDatePicker(year=todays_date.year,
        month=todays_date.month, day=todays_date.day)
        date_dialog.bind(on_save=
        lambda instance, value, x: self.date_chosen(instance, value, btn_id)
        )
        date_dialog.open()

    def show_theme_picker(self) :
        theme_dialog = MDThemePicker()
        theme_dialog.open()

    def save_memoir(self) :
        msg = self.root.ids.memoir_textField.text
        if msg != "" :
            # write the memoir to the JSON file
            store = JsonStore('memoir.json')

            # the max strategy is used because otherwise if a record from middle is deleted, store.count()+1 will return the 
            # key which is still present, and replacing it
            # e.g. 2 records with keys 1 and 2. Delete 1. store.count()+1 will return 2 the next time which is still there
            index = "1" if store.count() == 0 else str(max([int(key) for key in store])+1)  
            # index = str(store.count()+1)
            store.put(index, date=self.root.ids.date_button.text,
                    time=datetime.now().strftime('%H-%M-%S'), 
                    message=msg)
            
            self.root.ids.memoir_textField.text = ""   # empty the textField
            toast("Memoir saved successfully")

        else :
            self.dialog = MDDialog(title = "Message field cannot be left empty", md_bg_color=(1, 0.2, 0.2, 1),
                              buttons=[MDFlatButton(text="OK", on_release=self.close_dialogBox)])
            self.dialog.open()

    def read_memoir(self, second_time=False) :
        records_found = False

        keyword = self.root.ids.search_keyword.text
        # check if it is "SEARCH BY KEYWORD"
        if keyword != "":
            self.root.ids.reading_list_here.clear_widgets()
            store = JsonStore("memoir.json") 
            for key in store :
                dic = store.get(key)
                if re.search(keyword, dic["message"], re.IGNORECASE) :
                    list_item = TwoLineIconListItem(text=dic["message"], secondary_text=f"{dic['date']}   {dic['time']}",
                                                    on_release=self.reading_list_item_clicked)
                    list_item.add_widget(IconLeftWidget(icon="book"))
                    self.root.ids.reading_list_here.add_widget(list_item)
                    records_found = True

        # else find records in range
        else :
            # second time arg is there to be used when a record is deleted and there are no records left to read
            # the screen needs to turn back to the read screen with the dialog box
            from_date, to_date = datetime.strptime(self.root.ids.from_date_read.text[5:].strip(),"%d-%m-%Y"), datetime.strptime(self.root.ids.to_date_read.text[3:].strip(), "%d-%m-%Y")
            # check if to_date < from_date
            if from_date > to_date :
                # return a dialog box with error
                self.dialog = MDDialog(title="From_date can't be greater than To_date", text="Making them same.\nDone", md_bg_color=(1, 0.2, 0.2, 1),
                buttons=[MDFlatButton(text="OK", on_release=self.close_dialogBox)])
                self.dialog.open()
                # make both same.
                temp = self.root.ids.from_date_read.text[5:].strip()
                self.root.ids.to_date_read.text = f'TO:  {temp}'

            else :
                # first remove the previous list
                self.root.ids.reading_list_here.clear_widgets()

                # read the JSON file prepare the results
                store = JsonStore("memoir.json")
                for key in store :
                    dic = store.get(key)
                    date = datetime.strptime(dic["date"], "%d-%m-%Y")
                    if date >= from_date and date <= to_date :
                        # when a list item is clicked, open a dialog box
                        list_item = TwoLineIconListItem(text=dic["message"], secondary_text=f"{dic['date']}   {dic['time']}",
                                                        on_release=self.reading_list_item_clicked)
                        list_item.add_widget(IconLeftWidget(icon="book"))
                        self.root.ids.reading_list_here.add_widget(list_item)
                        records_found = True
            
        if records_found :
            # change screen 
            self.screen_change("reading_preview_screen")
        else :
            if second_time :
                self.screen_change("read_screen")
            toast("No records found")


    def reading_list_item_clicked(self, twolineiconlistitem) :
        self.reading_start_date, self.reading_start_time = twolineiconlistitem.secondary_text.split("   ")
        self.reading_message = twolineiconlistitem.text
        # check if it is searched by keyword or not
        keyword = self.root.ids.search_keyword.text
        
        # if total_words (excluding newline characters) is more than 60, print the msg on new screen, else 
        # print in the dialog box
        if len(self.reading_message.replace("\n", "")) > 60:
            if keyword != "" :
                msg = re.sub(f"({keyword})", f"[color=#8B0000][b][u]\\1[/u][/b][/color]", self.reading_message, flags=re.IGNORECASE)
                self.root.ids.message_message_here.text = f"Date: {self.reading_start_date}\nTime: {self.reading_start_time}\n\nMessage:\n{msg}"
            else :
                self.root.ids.message_message_here.text = f"Date: {self.reading_start_date}\nTime: {self.reading_start_time}\n\nMessage:\n{self.reading_message}"

            # change the screen
            self.root.ids.screen_manager.current = "long_memoir_reading_screen"
       
        else :
            if keyword != "" :
                msg = self.reading_message.replace(keyword, f"[color=#8B0000][b][u]{keyword}[/u][/b][/color]")
                self.dialog = MDDialog(text= f"Date: {self.reading_start_date}\nTime: {self.reading_start_time}\nMessage: {msg}", 
                        buttons=[MDRaisedButton(text="DELETE", md_bg_color=(1, 0.2, 0.2, 1),
                        on_release=self.deletion_confirmation), 
                        MDRaisedButton(text="Close", on_release=self.close_dialogBox)])
            else :
                self.dialog = MDDialog(text= f"Date: {self.reading_start_date}\nTime: {self.reading_start_time}\nMessage: {self.reading_message}", 
                        buttons=[MDRaisedButton(text="DELETE", md_bg_color=(1, 0.2, 0.2, 1),
                        on_release=self.deletion_confirmation), 
                        MDRaisedButton(text="Close", on_release=self.close_dialogBox)])

            self.dialog.open()

    def deletion_confirmation(self, obj=None) :
        # close the previous dialog box
        self.dialog.dismiss()
        self.dialog = MDDialog(title="Confirm?", 
        buttons=[MDRaisedButton(text="DELETE", md_bg_color=(1, 0.2, 0.2, 1), on_release=self.delete_single_record),
        MDFlatButton(text="Cancel", on_release=self.close_dialogBox)])
        self.dialog.open()

    def delete_single_record(self, obj) :
        store = JsonStore("memoir.json")
        # search the key and delete the record
        for key in store :
            val = store.get(key)
            if (val["date"] == self.reading_start_date) and (val["time"] == self.reading_start_time) and (val["message"] == self.reading_message) :
                # this is the key, delete it
                store.delete(key)
        # close the old dialog box
        self.dialog.dismiss()
        # run the read_memoir function again to refresh the list
        self.read_memoir(second_time=True)
        toast("Record deleted")

    def delete_memoir(self) :
        store = JsonStore("memoir.json")
        if "ALL" in self.root.ids.deletion_option.text :
            # all records need to be deleted
            if store.count() > 0 :
                self.dialog = MDDialog(title=f"{store.count()} records found. PERMANENTLY delete them all?",
                buttons=[MDFlatButton(text="Cancel", on_release=self.close_dialogBox),
                MDRaisedButton(text="DELETE", on_release=self.delete_all_records)])
                self.dialog.open()
            else :
                # if no records are found
                toast("No records found")

        else :
            # delete the records in range
            from_date, to_date = datetime.strptime(self.root.ids.from_date_delete.text[5:].strip(),"%d-%m-%Y"), datetime.strptime(self.root.ids.to_date_delete.text[3:].strip(), "%d-%m-%Y")
            row_data_deletion = []
            # check if from_date > to_date
            if from_date > to_date :
                # return a dialog box with error
                self.dialog = MDDialog(title="From_date can't be greater than To_date", text="Making them same.\nDone", md_bg_color=(1, 0.2, 0.2, 1),
                buttons=[MDFlatButton(text="OK", on_release=self.close_dialogBox)])
                self.dialog.open()
                # make both same
                temp = self.root.ids.from_date_read.text[5:].strip()
                self.root.ids.to_date_delete.text = f'TO:  {temp}'
            
            else:
                for key in store :
                    dic = store.get(key)
                    date = datetime.strptime(dic["date"], "%d-%m-%Y")
                    if date >= from_date and date <= to_date :
                        row_data_deletion.append((dic["date"], dic["message"], dic["time"], key))
                
                if len(row_data_deletion) > 0 :
                    # show deletion preview
                    self.show_deletion_preview(row_data_deletion)
                else :
                    # if no records are found
                    toast("No records found")

    def close_dialogBox(self, obj) :
        self.dialog.dismiss()

    def delete_all_records(self, obj) :
        store = JsonStore("memoir.json")
        for key in store :
            # delete the record
            store.delete(key)
        # close the dialog box
        self.dialog.dismiss()
        # show a confirmation dialog box
        toast("All records deleted")
            
    def show_deletion_preview(self, row_data_deletion) :
        # delete the previous table first
        self.root.ids.deletion_table_here.clear_widgets()

        # change the screen
        self.screen_change("deletion_preview_screen")
        # add a dummy row if there is only 1 record coz Kivy fucks up single row datatable
        if len(row_data_deletion) == 1 :
            row_data_deletion += [("", "", "", "")]

        self.deletiontable = MDDataTable(
            pos_hint= {"center_x":0.5, "center_y": 0.5},
            use_pagination=True,
            #rows_num= len(row_data_deletion),
            check= True,
            column_data= [("Date", dp(30)),("Message", dp(30)),("Time", dp(15)), ("Key", dp(20))],
            row_data= row_data_deletion
        )
        # add rows to the data
        self.root.ids.deletion_table_here.add_widget(self.deletiontable)

    def deleteInRange_warning(self) :
        records = self.deletiontable.get_row_checks() 
        count = 1 if len(records) == 2 and records[1][0] == "" else len(records)
        if len(records) > 0 and records[0][0] != "":   # the selected record cannot be only dummy record
            self.dialog = MDDialog(title=f"{count} will be PERMANENTLY DELETED. Proceed?", 
            buttons=[MDFlatButton(text="Cancel", on_release=self.close_dialogBox), 
            MDRaisedButton(text="DELETE", on_release=self.deleteInRange_confirmed)])
        else :
            toast("No record selected")

    def deleteInRange_confirmed(self, obj) :
        # close the dialog box
        self.dialog.dismiss()

        store = JsonStore("memoir.json")
        records = self.deletiontable.get_row_checks()

        for _, _, _, key in records :
            if key != "" :
                # delete all those records
                store.delete(key)
        # move back to the original deletion screen
        self.screen_change("delete_screen")

        # show a confirmation dialog box
        toast(f"{len(records)} records deleted successfully")


EMemoirApp().run()