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
              [sg.Text('SSN:', size=(10, 1)), sg.Input(size=(3, 1), key='id')],
              [sg.Text('Password:', size=(20, 1)), sg.Input(size=(20, 1), key='password')],
              [sg.Button('Login')],
              [sg.Exit()]]

    return sg.Window('Login Window', layout)

def login_check():
    global login_user_id
    global login_user_name
    global login_user_type
    global window

    uid = values['id']
    upass = values['password']
    if uid == '':
        sg.popup('SSN cannot be empty')
    elif upass == '':
        sg.popup('Password cannot be empty')
    else:
        # first check if this is a valid user
        cur.execute('SELECT SSN, UName, USurname FROM User WHERE SSN = ? AND Password = ?', (uid, upass))
        row = cur.fetchone()

        if row is None:
            sg.popup('ID or password is wrong!')
        else:
            # this is some existing user, let's keep the ID of this user in the global variable
            login_user_id = row[0]

            # we will use the name in the welcome message
            login_user_name = row[1] +" "+ row[2]

            # now let's find which type of user this login_user_id belongs to
            # let's first check if this is a student
            cur.execute('SELECT MSSN FROM Mentor WHERE MSSN = ?', (uid,))
            row_mentor = cur.fetchone()
            if row_mentor is not None:
                login_user_type = 'Mentor'

            else:
                sg.popup('No such mentor found')
                window.close()
                window=window_login()
            return (login_user_type)

def window_mentor():
    tributes = []
    # get name, id , status of tribute
    for row in cur.execute('''SELECT TributeID, TName, TSurname, Status
                                  FROM Tribute, Mentor
                                  WHERE MSSN=Mentor_SSN
                                  AND MSSN = ?''', (login_user_id,)):
        tributes.append(row)
    layout = [[sg.Text('Welcome ' + login_user_name)],
              [sg.Combo(tributes,size=(40,len(tributes)),key='chosen_tribute')],
              [sg.Button('Tribute Activity')],
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
def window_tribute_activity():
    pass

window=window_login()
while True:
    event, values = window.read()

    if (event == 'Login'):
        window.close()
        user_type = login_check() #determines user typr and existance of user
        if user_type == 'Mentor':
            window = window_mentor()

    if (event == 'Tribute Activity'):
        window.close()
        window = window_tribute_activity()

    if (event == 'See Pending Gifts'):
        window.close()
        window = window_gifts()

    if (event=='Logout'):
        window.close()
        window =window_login()

    if event == sg.WIN_CLOSED or event == 'Exit':
        break

window.close()