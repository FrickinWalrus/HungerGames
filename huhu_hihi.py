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
sg.theme('DarkBrown4')
def window_login():
    layout = [[sg.Text('Welcome to the Hunger Games Management System.', pad=((40,40),(0,5)), font='Helvetica 12 bold')],
              [sg.Text('Please enter your information.', pad=((0,0),(0,5)))],
              [sg.Text('SSN:', size=(10, 1), pad=((0,75),(0,0))), sg.Input(size=(20, 1), key='id')],
              [sg.Text('Password:', size=(20, 1), pad=((0,0),(0,15))), sg.Input(size=(20, 1), pad=((0,0),(0,15)), key='password')],
              [sg.Exit(),sg.Button('Login',pad=((400,0),(0,0)))]]

    return sg.Window('Login Window', layout, size=(500,160))

def login_check():
    global login_user_id
    global login_user_name
    global login_user_type
    global window

    uid = values['id']
    upass = values['password']
    if uid == '':
        sg.popup_no_buttons('SSN cannot be empty',title='Error',auto_close=True,auto_close_duration=5)
        window.close()
        window=window_login()
    elif upass == '':
        sg.popup_no_buttons('Password cannot be empty',title='Error',auto_close=True,auto_close_duration=5)
        window.close()
        window=window_login()
    else:
        # first check if this is a valid user
        cur.execute('SELECT SSN, UName, USurname FROM User WHERE SSN = ? AND Password = ?', (uid, upass))
        row = cur.fetchone()

        if row is None:
            sg.popup_no_buttons('ID/Password is incorrect.',title='Error',auto_close=True,auto_close_duration=5)
            window.close()
            window = window_login()
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
                sg.popup('No such mentor found.')
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
    layout = [[sg.Text('Welcome ' + login_user_name, font='Helvetica 12 bold', pad=(0,5))],
              [sg.Text('Choose a tribute:', pad=((0,0),(10,25))), sg.Combo(tributes,size=(40,len(tributes)), pad=((5,0),(10,25)),key='chosen_tribute')],
              [sg.Button('See Tribute Activity')],
              [sg.Button('See Gifts For The Tribute', pad=((5,192),(0,0))),sg.Button('Logout',)]]
    return sg.Window('Mentor Window', layout)


def window_gifts():
    gifts = getGifts(chosenTribute_G)
    layout = [[sg.Listbox(gifts, size=(80, 10), key='gift')],
              [sg.Button('Authorize')],
              [sg.Button('Return To Main')]]
    print("pipi", chosenTribute_G)
    return sg.Window('Gifts Window', layout), chosenTribute_G


def getGifts(tribute):
    gifts = []
    for row in cur.execute('''SELECT S.GiftName, S.Amount, S.Authorization, S.AuthorizationDate
                            FROM SendsGift S, Tribute T
                            WHERE S.TributeID = T.TributeID and T.Mentor_SSN = ? and T.TributeID = ? ''',
                            (login_user_id, tribute)):
        row = list(row)
        if row[2] == 1:
            row[2] = 'Authorized'
        else:
            row[2] = 'Pending'
        gifts.append(tuple(row))
    return gifts


def window_tribute_activity():
    activities = []
    chosen_tribute4activities = values['chosen_tribute'][0]
    #print(values)
    for row in cur.execute('''SELECT I.InteractionDate, T1.TName, T1.TSurname, I.Description, T2.TName, T2.TSurname
                              FROM Interaction I, Tribute T1, Tribute T2
                              WHERE I.SourceTribute = T1.TributeID
                                and I.TargetTribute = T2.TributeID 
                                and (T1.TributeID = ? or T2.TributeID = ?)
                              ORDER BY I.InteractionDate DESC''',
                           (chosen_tribute4activities, chosen_tribute4activities)):
        activities.append(row)
    #print(activities)  # for debug purposes
    layout = [[sg.Listbox(activities, size=(100, 10), key='activities')],
              [sg.Button('Return To Main')]]
    return sg.Window('Gifts Window', layout)

# ----------- MAIN CODE -----------
window = window_login()
while True:
    event, values = window.read()

    if event == 'Login':
        window.close()
        user_type = login_check() #determines user typr and existance of user
        if user_type == 'Mentor':
            window = window_mentor()

    elif event == 'See Tribute Activity':
        window.close()
        window = window_tribute_activity()

    elif event == 'See Gifts For The Tribute':
        chosenTribute_G = values['chosen_tribute'][0]
        window.close()
        window, chosenTribute_G = window_gifts()

    elif event == 'Logout':
        window.close()
        window = window_login()

    elif event == "Authorize":
        gift = values['gift']
        if gift == []:
            sg.popup_no_buttons("Please select a gift to authorize.", title='', auto_close=True, auto_close_duration=2)
        else:
            if gift[0][2] == 1: # if the gift is already authorized
                sg.popup_no_buttons("The gift is already authorized.",title='',auto_close=True,auto_close_duration=5)
            else:
                cur.execute('UPDATE SendsGift SET Authorization = ? WHERE TributeID = ? and GiftName = ?', (True, chosenTribute_G, gift[0][0])) # Update query for SQL
                window.Element('gift').Update(values=getGifts(chosenTribute_G)) # Finally update and re-display

    elif event == 'Return To Main':
        if login_user_type == 'Mentor':
            window.close()
            window = window_mentor()
        else:
            window.close()
            window = window_login()

    elif event == sg.WIN_CLOSED or event == 'Exit':
        break

window.close()