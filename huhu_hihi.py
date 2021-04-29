# import
import random
import os
import sqlite3
import PySimpleGUI as sg
from datetime import datetime
ProjectFolder = os.path.abspath(os.path.join(os.path.abspath(os.getcwd())))
directory_name = os.path.dirname
dbFolder = os.path.abspath(os.path.join(os.path.abspath(os.getcwd()), "database/Implementation1.db"))
# connect to the DB
con = sqlite3.connect(dbFolder)
cur = con.cursor()

# global variables
login_user_id = -1
login_user_name = -1
login_user_type = -1


# window functions
def window_login():
    layout = [[sg.Text('Welcome to the Hunger Games Management System. Please enter your information.')],
              [sg.Text('ID:', size=(10, 1)), sg.Input(size=(3, 1), key='id')],
              [sg.Text('Password:', size=(20, 1)), sg.Input(size=(20, 1), key='password')],
              [sg.Button('Login')]]

    return sg.Window('Login Window', layout)


def window_mentor():
    layout = [[sg.Text('Welcome ' + login_user_name)],
              [sg.Button('Tribute Status')],
              [sg.Button('See Pending Gifts')],
              [sg.Button('Logout')]]

    return sg.Window('Mentor Window', layout)


def window_gifts():
    gifts = []

    for row in cur.execute('''SELECT *
                              FROM SendsGift S, Tribute T
                              WHERE S.TributeID = T.TributeID and T.Mentor_SSN = ?''', (login_user_id,)):
        gifts.append(row)

    layout = [[sg.Text('Your Tributes:'), sg.Combo(gifts, size=(25, 7), key='tribute'), sg.Button('List Tributes')],
              [sg.Listbox((), size=(40, 10), key='student')],
              [sg.Text('Grade: '), sg.Input(key='grade'), sg.Button('Update Grade')],
              [sg.Button('Return To Main')]]

    return sg.Window('Grade Window', layout)
