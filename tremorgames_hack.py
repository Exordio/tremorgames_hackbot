import getpass
import time
import hashlib
import json
import random
import requests
import numpy as np
import pandas as pd

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

csf_File = 'csvdata.csv'

data_Array = np.delete(np.genfromtxt(csf_File, delimiter=',', dtype = None), (0), axis= 0) # загрузка данных из csv 

def IsNumeric( v ):
    try:
        v2 = int( v )
        return True
    except (ValueError, TypeError):
        return False

def LoginTremorGames( s, username, password ):
    s.headers.update( { 'Origin': 'http://www.tremorgames.com' } )
    s.headers.pop( 'X-Requested-With', None )
    s.headers.update( { 'Referer': 'http://www.tremorgames.com/index.php' } )
    r = s.post( 'http://www.tremorgames.com/index.php', data={ 'loginuser': username, 'loginpassword': password, 'Submit': '' }, allow_redirects=False )
    return

def GetUserCoins( s ):
    s.headers.pop( 'Origin', None )
    s.headers.update( { 'X-Requested-With': 'XMLHttpRequest' } )
    s.headers.update( { 'Referer': GameURL } )
    r = s.get( 'http://www.tremorgames.com/achievements/ajax_getusercoins.php' )
    return int( r.text )

def GetGameAchievements( s ):
    s.headers.pop( 'Origin', None )
    s.headers.pop( 'X-Requested-With', None )
    s.headers.pop( 'Referer', None )
    r = s.get( GameURL, allow_redirects=False )

    jsonStartIdx = r.text.find( 'AchievementsJS = jQuery.parseJSON(\'' ) + len( 'AchievementsJS = jQuery.parseJSON(\'' )
    jsonEndIdx = r.text.find( '\');', jsonStartIdx )

    return json.loads( r.text[jsonStartIdx:jsonEndIdx] )

def GetGameStats( s, playerName ):
    s.headers.pop( 'Origin', None )
    s.headers.update( { 'X-Requested-With': 'ShockwaveFlash/24.0.0.194' } )
    s.headers.update( { 'Referer': GameURL } )
    r = s.get( 'http://www.tremorgames.com/achievements/json_get_stats.php', params={ 'PlayerName': playerName, 'GameID': GameID } )
    return r.json()

def UpdateGameStat( s, playerName, statName, statValue ):
    # calculate key
    requestKey = hashlib.md5( (playerName + Key + str( statValue )).encode( 'utf-8' ) ).hexdigest().lower()

    s.headers.update( { 'Origin': 'http://www.tremorgames.com' } )
    s.headers.update( { 'X-Requested-With': 'ShockwaveFlash/24.0.0.194' } )
    s.headers.update( { 'Referer': GameSWF } )
    r = s.post( 'http://www.tremorgames.com/achievements/record_stats.php', data={ 'StatValue': statValue, 'StatName': statName, 'PlayerName': playerName, 'GameID': GameID, 'Key': requestKey } )
    return

random.seed()
s = requests.Session()
s.headers.update( { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36' } )
s.headers.update( { 'Accept-Language': 'en-US,en;q=0.8' } )

# Логин на т емо 
username = input( 'Логин на tremor : ' )
password = input( 'Pass : ' )
LoginTremorGames( s, username, password )
print( 'Вошли' )
i = 0
while i < 166:
    GameID = int(data_Array[i,2])
    Key = (data_Array[i,3])
    GameURL = (data_Array[i,0])
    GameSWF = (data_Array[i,1])
    gameAchievements = GetGameAchievements( s )
#gameStats = GetGameStats( s, username )

# Начало фарма ачивок
    for achievement in gameAchievements:
        # currently only Max and Cumulative stat types supported
        if achievement['StatType'] != 'Max' and achievement['StatType'] != 'Cumulative':
            continue

    # usually the current stat value isn't 0 but something like null or none, so we set it to 0
        if not IsNumeric( achievement['ProgressValue'] ):
            achievement['ProgressValue'] = '0'

        statIncrease = 1
        statGoal = int( achievement['StatValue'] )
        if statGoal >= 100000:
            statIncrease = random.randrange( 1, 10000 )
        elif statGoal >= 10000:
            statIncrease = random.randrange( 1, 1000 )
        elif statGoal >= 1000:
            statIncrease = random.randrange( 1, 100 )

        print( 'Сейчас выполняется ачивка -  "' + achievement['AchievementName'] + '"' )
        while int( achievement['ProgressValue'] ) < int( achievement['StatValue'] ):
            achievement['ProgressValue'] = str( int( achievement['ProgressValue'] ) + statIncrease )

            if achievement['StatType'] == 'Cumulative':
                UpdateGameStat( s, username, achievement['StatName'], statIncrease )
            else:
                UpdateGameStat( s, username, achievement['StatName'], int( achievement['ProgressValue'] ) )

        # so we don't do it too fast
            time.sleep( 1 )

        print( 'Ачивка получена\n' )
    print( 'Игра закончена, по счёту она : ',i+1 )#;print ( '1');time.sleep( 1 );print ( '2');time.sleep( 1 );print ( '3');time.sleep( 1 );print ( '4');time.sleep( 1 );print ( '5')
    i = i + 1
i = 0

print( 'END' )