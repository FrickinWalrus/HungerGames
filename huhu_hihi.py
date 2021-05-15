# import
import random
import numpy as np
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
#ayceayce
            if row_mentor is None:
                #not a mentor, check for game maker
                cur.execute('SELECT GameMakerSSN FROM GameMaker WHERE GameMakerSSN = ?', (uid,))
                row_gamemaker = cur.fetchone()
                if row_gamemaker is None:
                    #not a game maker, check for sponsor, dusdus
                    cur.execute('SELECT SpSSN FROM Sponsor WHERE SpSSN = ?', (uid,))
                    row_sponsor = cur.fetchone()
                    if row_sponsor is None:
                        sg.popup('User type error! Please contact the admin.')
                        window.close()
                        window = window_login()
                    else:
                        login_user_type= 'Sponsor'
                        sg.popup('Welcome, ' + login_user_name + ' (Sponsor)')
                        window.close()
                        window = window_sponsor()
                else:
                    login_user_type = 'Game Maker'
                    sg.popup('Welcome, ' + login_user_name + ' (Game Maker)')
                    window.close()
                    window = window_gamemaker()
            else:
                login_user_type = 'Mentor'
                sg.popup('Welcome, ' + login_user_name + ' (Mentor)')
                window.close()
                window = window_mentor()
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
              [sg.Button('See Gifts For The Tribute', pad=((5,192),(0,0))),sg.Button('Logout',)],
              [sg.Button('My Awards')]]
    return sg.Window('Mentor Window', layout)


def window_gifts():
    gifts = getGifts(chosenTribute_G)
    layout = [[sg.Listbox(values=gifts, size=(80, 10), key='gift')],
              [sg.Button('Authorize')],
              [sg.Button('Return To Main')]]
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
def my_awards():
    awards=[]
    for row in cur.execute('''SELECT AwardName
                                  FROM ReceiveAward
                                  WHERE MentorSSN = ?''', (login_user_id,)):
        awards.append(row)
    layout = [[sg.Text('Your Received Awards', font='Helvetica 12 bold', pad=(0, 5))],
              [sg.Listbox(awards, size=(80, 10), key='rule')],
              [sg.Button('Return To Main'), sg.Button('Logout', )]]
    return sg.Window('Game Maker Window', layout)

#ayceayce
def window_gamemaker():

    layout = [[sg.Text('Welcome ' + login_user_name, font='Helvetica 12 bold', pad=(0,5))],
              [sg.Button('Games')],
              [sg.Button('Mentors')],
              [sg.Button('Record Interaction', pad=((5,192),(0,0)))],
              [sg.Button('Change Tribute Status', pad=((5,192),(0,0)))],
              [sg.Button('Logout',)]]
    return sg.Window('Game Maker Window', layout)

def window_games():
    games = []
    # get name, id , status of tribute
    for row in cur.execute('''SELECT Year, Description
                                  FROM GameWithAdmin
                                  '''):
        games.append(row)

    layout = [[sg.Text('Choose a game:', pad=((0,0),(10,25))), sg.Combo(games,size=(40,len(games)), pad=((5,0),(10,25)),key='chosen_game'), sg.Button("See Rules")],
              [sg.Listbox(values, size=(80, 10), key='rule')],
              [sg.Text('New Rule: '), sg.Input(key='new_rule'), sg.Button('Set a new rule')],
              [sg.Button('Return To Main')]]
    return sg.Window("Game Window", layout)

def button_see_rules(values):
    game = values["chosen_game"]
    if game == "":
        sg.popup("Please choose a game")
    else:
        game_year = game[0]
        rules = []

        for row in cur.execute('''SELECT Rule_Year, Content
                                      FROM AddsRules
                                      WHERE Rule_Year = ?''', (game_year,)):
            rules.append(row)
        window.Element("rule").Update(values=rules)

def button_set_rule(values):
    newrule = values["new_rule"]
    year = values["chosen_game"][0]
    cur.execute('INSERT INTO AddsRules VALUES (?,?,?)', (login_user_id, year, newrule))
    window.Element('new_rule').Update(value="")
    sg.popup("New rule added successfully!")

    ruless = []
    for row in cur.execute('''SELECT Rule_Year, Content
                                  FROM AddsRules
                                  WHERE Rule_Year = ?''', (year,)):
        ruless.append(row)

    window.Element("rule").Update(values=ruless)

def window_award():
    mentors = []
    for row in cur.execute('''SELECT u.SSN, u.UName, u.USurname
                                  FROM Mentor m, User u
                                  WHERE m.MSSN=u.SSN
                                  '''):
        mentors.append(row)

    layout = [[sg.Text('Choose a mentor:', pad=((0,0),(10,25))), sg.Combo(mentors,size=(40,len(mentors)), pad=((5,0),(10,25)),key='chosen_mentor')],
              [sg.Text('Name of the Award:'), sg.Input(key='award_name')],
              [sg.Button("Give Award")],
              [sg.Button('Return To Main')]]

    return sg.Window('Award Window', layout)

def window_interaction():
    all_tributes = []
    for row in cur.execute('''SELECT TributeID, TName, TSurname
                                  FROM Tribute
                                  WHERE Status<>"Dead"
                                  '''):
        all_tributes.append(row)

    layout = [[sg.Text('Choose a source tribute:', pad=((0,0),(10,25))), sg.Combo(all_tributes, size=(40,len(all_tributes)), pad=((5,0),(10,25)),key='chosen_st')],
              [sg.Text('Choose a target tribute:', pad=((0, 0), (10, 25))),sg.Combo(all_tributes, size=(40, len(all_tributes)), pad=((5, 0), (10, 25)), key='chosen_tt')],
              [sg.Text('New Interaction: '), sg.Input(key='new_interaction')],
              #[sg.Text('Enter the date of interaction.'),sg.CalendarButton("Pick date",key="date", format='%Y:%m:%d'),
               [sg.Text('Enter the date of interaction.'),sg.Input(key='date'),sg.Text('Time: '), sg.Input(key='time')],
              [sg.Button('Record a new Interaction'),sg.Button('Return To Main')]]
    return sg.Window('Interaction Window', layout)
#ayceayce
#dusdus
def button_give_award(values):
    award_mentor = values['chosen_mentor'][0]
    award_name = values['award_name']
    cur.execute('INSERT INTO ReceiveAward VALUES (?,?)',(award_name,award_mentor))
    sg.popup("Award given to chosen Mentor!")
    window.Element('award_name').Update(value='')

def window_trb_status():
    all_tributes = []
    all_status=['Alive','Dead','Injured']
    for row in cur.execute('''SELECT TributeID, TName, TSurname,Status
                                      FROM Tribute'''):
        all_tributes.append(row)
    layout = [[sg.Text('Choose a tribute:', pad=((0,0),(10,25))), sg.Listbox(all_tributes, size=(40,len(all_tributes)), pad=((5,0),(10,25)),key='chosen_trb')],
             [sg.Text('Possible Status'), sg.Listbox(all_status,key='chosen_stat'),sg.Button('Set Status')],
              [sg.Button('Return To Main')]]
    return sg.Window('Tribute Status Window', layout)

def set_status():
    if values['chosen_trb'] == []:
        sg.popup_no_buttons("Please select a tribute.", title='', auto_close=True, auto_close_duration=2)
    elif values['chosen_stat']==[]:
        sg.popup_no_buttons("Please select status.", title='', auto_close=True, auto_close_duration=2)
    else:
        if values['chosen_stat'][0]==values['chosen_trb'][0][3]:
            sg.popup_no_buttons('The status is not changed', title='', auto_close=True, auto_close_duration=2)
        else:
            cur.execute('UPDATE Tribute SET Status = ? WHERE TributeID=?',(values['chosen_stat'][0],values['chosen_trb'][0][0]))
            sg.popup_no_buttons('The status is changed', title='', auto_close=True, auto_close_duration=2)

def window_sponsor():
    credit_card_no = []
    tribute_spo = []
    available_gifts = []
    for row in cur.execute('''SELECT TName
                                     FROM Tribute
                                   '''):
        tribute_spo.append(row)
    tribute_spo.append('')
    for row2 in cur.execute('''SELECT *
                                            FROM Gift
                                           '''):
        available_gifts.append(row2)

    for row3 in cur.execute('''SELECT CardNumber
                                         FROM Sponsor
                                         WHERE SpSSN= ?''', (login_user_id,)):
        credit_card_no.append(row3[0])
    tribute_spo = list(set(tribute_spo))


    layout = [[sg.Text('Welcome ' + login_user_name, font='Helvetica 12 bold', pad=(0,5))],
              [sg.Text('Your Credit Card Number:'+ str(credit_card_no[0])), sg.Button('Update')],
              [sg.Text('Filter Tributes By')],
              [sg.Text('Game:'), sg.Combo(values=['2021','2020', ''], key='chosen_game'),sg.Text('Status:'),sg.Combo(values=['Dead', 'Alive','Injured',''], key='chosen_status'),sg.Text('District:'),sg.Combo(values=['1','2','3','5','6',''], key='chosen_district'),sg.Text('Name:'),sg.Combo(tribute_spo, key='chosen_name'),sg.Button('List Tributes')],
              [sg.Listbox((),size=(40, 10),key='tribute4gift')],
              [sg.Text('Choose a gift:', pad=((0, 0), (10, 25))),sg.Combo(available_gifts, size=(40, len(available_gifts)), pad=((5, 0), (10, 25)), key='gift4tribute'),
               sg.Text(' Enter amount:', pad=((0, 0), (10, 25))),sg.Input(key='gift_amount',pad=((5, 0), (10, 25)),size=(10, 10))],
              [sg.Button('Send Gift'), sg.Button('Logout')]]
    return sg.Window('Sponsor Login', layout)


def button_list_tributes(values):
    game = values['chosen_game']
    district = values['chosen_district']
    status = values['chosen_status']
    name = values['chosen_name']
    filter_result = []


    if len(name) == 0 and len(district) == 0 and len(status) == 0 and len(game) ==0:

        for row in cur.execute('''SELECT TributeID, TName, TSurname, DistrictID
                                         FROM Tribute
                                        '''):
            filter_result.append(row)

    elif len(name) == 0 and len(game) != 0 and len(status) != 0 and len(district) != 0:
        filter_result = []
        for row in cur.execute('''SELECT TributeID, TName, TSurname, DistrictID
                                                       FROM Tribute
                                                       WHERE Game_year= ? and Status=? and DistrictID=?''',
                               (game, status, district)):
            filter_result.append(row)

    elif len(name)== 0 and len(district)== 0:
        if len(game) == 0:
            filter_result = []
            for row in cur.execute('''SELECT TributeID, TName, TSurname, DistrictID
                                                                        FROM Tribute
                                                                        WHERE Status=?''', (status,)):
                filter_result.append(row)
        elif len(status) == 0:

            filter_result = []
            for row in cur.execute('''SELECT TributeID, TName, TSurname, DistrictID
                                                     FROM Tribute
                                                     WHERE Game_year= ?''', (game,)):
                filter_result.append(row)
        else:
            filter_result = []
            for row in cur.execute('''SELECT TributeID, TName, TSurname, DistrictID
                                                     FROM Tribute
                                                     WHERE Game_year= ? and Status=?''', (game,status)):
                filter_result.append(row)

    elif len(name) == 0 and len(status) == 0 and len(game) != 0 and len(district) != 0:
        filter_result = []
        for row in cur.execute('''SELECT TributeID, TName, TSurname, DistrictID
                                                            FROM Tribute
                                                            WHERE Game_year= ? and DistrictID=?''', (game,  district)):
            filter_result.append(row)


    elif len(name) == 0 and len(game)== 0 and len(status)== 0 and len(district) != 0:

        filter_result = []
        for row in cur.execute('''SELECT TributeID, TName, TSurname, DistrictID
                                                                    FROM Tribute
                                                                    WHERE DistrictID=?''', (district,)):
            filter_result.append(row)

    elif len(name) == 0 and len(game)== 0 and len(status) != 0 and len(district) != 0:
        filter_result = []
        for row in cur.execute('''SELECT TributeID, TName, TSurname, DistrictID
                                                            FROM Tribute
                                                            WHERE Status=? and DistrictID=?''', (status,  district)):
            filter_result.append(row)

    else:
        if len(game) == 0 and len(status) == 0 and len(district) == 0:
            filter_result = []
            for row in cur.execute('''SELECT TributeID, TName, TSurname, DistrictID
                                        FROM Tribute
                                        WHERE TName=?''',
                                   (list(name)[0], )):
                filter_result.append(row)

        if len(game) == 0 and len(status) == 0 and len(district) != 0:
            filter_result = []
            for row in cur.execute('''SELECT TributeID, TName, TSurname, DistrictID
                                        FROM Tribute
                                        WHERE DistrictID=? and TName=?''',
                                   (district,list(name)[0] )):
                filter_result.append(row)

        if len(game) == 0 and len(status) != 0 and len(district) == 0:
            filter_result = []
            for row in cur.execute('''SELECT TributeID, TName, TSurname, DistrictID
                                        FROM Tribute
                                        WHERE Status=? and TName=?''',
                                   (status,list(name)[0])):
                filter_result.append(row)

        if len(game) == 0 and len(status) != 0 and len(district) != 0:
            filter_result = []
            for row in cur.execute('''SELECT TributeID, TName, TSurname, DistrictID
                                                                                FROM Tribute
                                                                                WHERE TName=? and Status=? and DistrictID=?''', (list(name)[0],status,  district)):
                filter_result.append(row)
        
        if len(game) != 0 and len(status) != 0 and len(district) != 0:
            filter_result = []
            for row in cur.execute('''SELECT TributeID, TName, TSurname, DistrictID
                                                                                FROM Tribute
                                                                                WHERE TName=? and Game_year= ? and Status=? and DistrictID=?''',
                                   (list(name)[0], game, status, district)):
                filter_result.append(row)
        if len(game) != 0 and len(status) == 0 and len(district) != 0:
            filter_result = []
            for row in cur.execute('''SELECT TributeID, TName, TSurname, DistrictID
                                                                                FROM Tribute
                                                                                WHERE TName=? and Game_year= ? and DistrictID=?''', (list(name)[0], game,  district)):
                filter_result.append(row)
        if len(game) != 0 and len(status) != 0 and len(district) == 0:
            filter_result = []
            for row in cur.execute('''SELECT TributeID, TName, TSurname, DistrictID
                                        FROM Tribute
                                        WHERE Game_year= ? and Status=? and TName=?''',
                                   (game,status, list(name)[0], )):
                filter_result.append(row)

        if len(game) != 0 and len(status) == 0 and len(district) == 0:
            filter_result = []
            for row in cur.execute('''SELECT TributeID, TName, TSurname, DistrictID
                                        FROM Tribute
                                        WHERE Game_year= ? and TName=?''',
                                   (game, list(name)[0], )):
                filter_result.append(row)

    window.Element('tribute4gift').Update(values=filter_result)

def button_send_gift(values):
    tribute = values['tribute4gift']
    gift = values['gift4tribute']
    g_amount=values['gift_amount']
    cur.execute('''SELECT Status
            FROM Tribute
            WHERE TributeID=?''', (values['tribute4gift'][0][0],))
    status = cur.fetchone()
    if status[0]=='Dead':  # the dead tributes can not receive gifts
        sg.popup_no_buttons("You can not send gifts to deceased tributes.", title='', auto_close=True,
                        auto_close_duration=2)
    elif g_amount=='':
        sg.popup_no_buttons("Please enter amount.", title='', auto_close=True,
                            auto_close_duration=2)
    else:
        try:
            amount=int(g_amount[0])
            cur.execute('INSERT INTO SendsGift VALUES (?,?,?,?,?,?)', (gift[0], login_user_id, tribute[0][0], g_amount[0], None, False))
            price=gift[1]*amount
            sg.popup("Your Gift has been added to the Pending List! Total cost: "+str(price)+" dollars")
            window.Element('tribute4gift').Update(values=[])
            window.Element('gift4tribute').Update(value='')
        except:
            sg.popup_no_buttons("Please enter an integer for amount.", title='', auto_close=True,
                                auto_close_duration=2)

def window_update_credit_card():

    layout = [[sg.Text('Please enter your new Credit Card Number:'), sg.Input(key='new_credit_card_no')],
              [sg.Button('Update My Credit Card Number')],
              [sg.Button('Return To Main')]]
    return sg.Window('Update Credit Card Number', layout)

#dusdus

# ----------- MAIN CODE -----------
window = window_login()
while True:
    event, values = window.read()

    if event == 'Login':
        window.close()
        user_type = login_check() #determines user type and existance of user
        if user_type == 'Mentor':
            window = window_mentor()

    elif event == 'See Tribute Activity':
        print(values)
        if values['chosen_tribute'] == '':
            sg.popup_no_buttons("Please select a tribute.", title='', auto_close=True, auto_close_duration=2)
        else:
            window.close()
            window = window_tribute_activity()

    elif event=='My Awards': # mentors can see their received awards
        window.close()
        window=my_awards()

    elif event == 'See Gifts For The Tribute':
        if values['chosen_tribute'] == '':
            sg.popup_no_buttons("Please select a tribute.", title='', auto_close=True, auto_close_duration=2)
        else:
            chosenTribute_G = values['chosen_tribute'][0]
            window.close()
            window, chosenTribute_G = window_gifts()
#ayceayce
    elif event == "Games":
            window.close()
            window = window_games()

    elif event == "See Rules":
        button_see_rules(values)

    elif event == 'Logout':
        window.close()
        window = window_login()
    elif event == 'Set a new rule':
        button_set_rule(values)
#ayceayce
#dusdus
    elif event == "Mentors":
        window.close()
        window = window_award()

    elif event == "Give Award":
        if values['chosen_mentor'] == '':
            sg.popup_no_buttons("Please select a mentor.", title='',auto_close=True, auto_close_duration=2)
        else:
            button_give_award(values)

    elif event == "Record Interaction":
        window.close()
        window = window_interaction()

    elif event == "Record a new Interaction":
        if values['date']=='':
            interactionDate = datetime.now()
            interactionDate = interactionDate.strftime('%Y-%m-%d %H:%M')
        else:
            date=values['date']
            time=values['time']
            interactionDate=date+' '+time

        new_interaction = values['new_interaction']
        source_tribute = values['chosen_st']
        target_tribute = values['chosen_tt']

        if not source_tribute:
            sg.popup_no_buttons("Please choose a source tribute.", title='', auto_close=True, auto_close_duration=2)
        elif not target_tribute:
            sg.popup_no_buttons("Please choose a target tribute.", title='', auto_close=True, auto_close_duration=2)
        elif new_interaction == '':
            sg.popup_no_buttons("Please enter a valid interaction.", title='',auto_close=True, auto_close_duration=2)
        else:
            cur.execute('INSERT INTO Interaction VALUES (?,?,?,?)', (interactionDate,new_interaction,source_tribute[0] ,target_tribute[0]))
            sg.popup('Tribute Activity Recorded.')
            window.Element('new_interaction').Update(value='')
            window.Element('chosen_st').Update(value='')
            window.Element('chosen_tt').Update(value='')
    elif event=='Change Tribute Status': # game makers can change the status of tributes
        window.close()
        window = window_trb_status()
    elif event=='Set Status': #set status alive, dead, injured
        set_status()
        window.close() # in order to clean but cause glitching
        window=window_trb_status()
    elif event == 'List Tributes':
        button_list_tributes(values)

    elif event == 'Send Gift':
        if not values['tribute4gift']:
            sg.popup_no_buttons("Please choose a tribute.", title='', auto_close=True, auto_close_duration=2)
        elif not values['gift4tribute']:
            sg.popup_no_buttons("Please choose a gift.", title='', auto_close=True, auto_close_duration=2)
        else:
            button_send_gift(values)
            window.close()  # in order to clean but causes glitching,can be taken out
            window=window_sponsor()

    elif event == 'Update':
        window.close()
        window = window_update_credit_card()

    elif event == 'Update My Credit Card Number':
        new_cc_no = values['new_credit_card_no']
        #print(len(str(new_cc_no)))
        if new_cc_no.isnumeric():
            if len(str(new_cc_no)) == 16:
                cur.execute('UPDATE Sponsor SET CardNumber = ? WHERE SpSSN = ?',(new_cc_no,login_user_id))
                sg.popup('Your Credit Card NUmber is Updated!')
                window.Element('new_credit_card_no').Update(value='')
            else:
                sg.popup_no_buttons("A Valid Credit Card Number should contain 16 numbers.", title='')
                window.Element('new_credit_card_no').Update(value='')
        else:
            sg.popup_no_buttons("Enter a valid Credit Card Number consisting of numbers.", title='')
            window.Element('new_credit_card_no').Update(value='')

#dusdus

    elif event == "Authorize":
        giftDate = datetime.now()
        giftDate = giftDate.strftime('%Y-%m-%d %H:%M:%S"')
        gift = values['gift']
        if gift == []:
            sg.popup_no_buttons("Please select a gift to authorize.", title='', auto_close=True, auto_close_duration=2)
        else:
            if gift[0][2] == 'Authorized': # if the gift is already authorized
                sg.popup_no_buttons("The gift is already authorized.",title='',auto_close=True,auto_close_duration=5)
            else:
                cur.execute('UPDATE SendsGift SET Authorization = ?, AuthorizationDate = ? WHERE TributeID = ? and GiftName = ?', (True, giftDate, chosenTribute_G, gift[0][0])) # Update query for SQL
                window.Element('gift').Update(values=getGifts(chosenTribute_G)) # Finally update and re-display

    elif event == 'Return To Main':
        if login_user_type == 'Mentor':
            window.close()
            window = window_mentor()
        elif login_user_type == 'Game Maker':
            window.close()
            window = window_gamemaker()
        elif login_user_type == 'Sponsor':
            window.close()
            window = window_sponsor()
        else:
            window.close()
            window = window_login()

    elif event == sg.WIN_CLOSED or event == 'Exit':
        break

window.close()