from spotipy.oauth2 import SpotifyOAuth
from recnetlogin import RecNetLogin
from dotenv import load_dotenv
import configparser
import sched, time
import requests
import spotipy
import sys
import os
import datetime

# ill be honest i dont remeber what this does all i know if i delete it it doesnt work
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def writeconfig():
    with open("config.ini", 'w') as f: 
        config.write(f)
    pass

#reading the config file, loading the env
config = configparser.ConfigParser()
config.read("config.ini")
load_dotenv(resource_path('.env'))
sc = sched.scheduler(time.time, time.sleep)

# checking if theres a config file, making one if theres not
try: 
    print(config['DONTCHANGE']['config_check'])
except:
    print('No config file found')
    print('Creating plain config file...')
    config = configparser.ConfigParser()

    config.add_section('DONTCHANGE')
    config['DONTCHANGE']['config_check'] = 'Config file found.'
    config['DONTCHANGE']['song_compare'] = 'placeholder'
    config.add_section('BIO')
    config['BIO']['bio'] = ''

    config.add_section('LOGIN')
    config['LOGIN']['storelogin'] = 'false'
    config['LOGIN']['YOURUSERNAME'] = ''
    config['LOGIN']['YOURPASSWORD'] = ''
    writeconfig()


#getting users username/password
if config.getboolean('LOGIN', 'storelogin') == True:
    YOURUSERNAME = config['LOGIN']['YOURUSERNAME']
    YOURPASSWORD = config['LOGIN']['YOURPASSWORD']
    use_found_login = input('Found login would you like to use?')
    while use_found_login not in {'y', 'n'}:
        print('Enter y/n')
        use_found_login = input('Found login would you like to use?')
    if use_found_login == 'n': 
        YOURUSERNAME = (input('Username: ')).lower()
        YOURPASSWORD = (input('Password: '))
        passwordconfirm = (input(f'You entered {YOURUSERNAME} as your username and {YOURPASSWORD} as your password, confirm(y)?'))
        while passwordconfirm != 'y':
            YOURUSERNAME = (input('Username: ')).lower()
            YOURPASSWORD = (input('Password: '))
            passwordconfirm = (input(f'You entered {YOURUSERNAME} as your username and {YOURPASSWORD} as your password, confirm(y)?'))
        storelogin = input('Would you like your login to be stored for next time(y/n)? ')
        while storelogin not in {'y', 'n'}:
            print('Enter y/n')
            storelogin = input('Would you like your login to be stored for next time(y/n)? ')
        if storelogin == 'y':
            config['LOGIN']['storelogin'] = 'true'
            config['LOGIN']['YOURUSERNAME'] = YOURUSERNAME
            config['LOGIN']['YOURPASSWORD'] = YOURPASSWORD
            writeconfig()
else:
    print('Enter the username/password of your account!')
    YOURUSERNAME = (input('Username: ')).lower()
    YOURPASSWORD = (input('Password: '))
    passwordconfirm = (input(f'You entered {YOURUSERNAME} as your username and {YOURPASSWORD} as your password, confirm(y)?'))
    while passwordconfirm != 'y':
        YOURUSERNAME = (input('Username: ')).lower()
        YOURPASSWORD = (input('Password: '))
        passwordconfirm = (input(f'You entered {YOURUSERNAME} as your username and {YOURPASSWORD} as your password, confirm(y)?'))
    storelogin = input('Would you like your login to be stored for next time(y/n)? ')
    while storelogin not in {'y', 'n'}:
        print('Enter y/n')
        storelogin = input('Would you like your login to be stored for next time(y/n)? ')
    if storelogin == 'y':
        config['LOGIN']['storelogin'] = 'true'
        config['LOGIN']['YOURUSERNAME'] = YOURUSERNAME
        config['LOGIN']['YOURPASSWORD'] = YOURPASSWORD
        writeconfig()
        
accountid_resp = requests.get(f'https://accounts.rec.net/account?username={YOURUSERNAME}')
accountid_resp_json = accountid_resp.json()
accountId = accountid_resp_json['accountId']

#setting spotipy auth stuff
client_id = os.environ['client_id']
client_secret = os.environ['client_secret']
redirect_uri = 'http://localhost:7777/callback'
scope = 'user-read-playback-state'

#recroom login 
def login(YOURUSERNAME, YOURPASSWORD):
  rnl = RecNetLogin(username=YOURUSERNAME, password=YOURPASSWORD)
  token = rnl.get_token(include_bearer=True)
  return token
token = login(YOURUSERNAME, YOURPASSWORD)


def song_info(scope, client_id, client_secret, redirect_uri):
    
    #authorizationing to spotify with spotipy
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        scope=scope,
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri)
    )

    #currently playing song request
    spotify_song_resp = sp.current_user_playing_track()

    #check to see if song is being played and handling for if not
    if spotify_song_resp != None or spotify_song_resp['is_playing'] != False:
        # spotify device request to get the volume
        spotify_device_resp = sp.devices()

        #format the song name 
        track_name = spotify_song_resp['item']['name']
        artists = [artist for artist in spotify_song_resp['item']['artists']]
        artist_names = ', '.join([artist['name'] for artist in artists])
        song = f'{track_name} by {artist_names}!'
        if len(song) < 32:
            song = song[:-3]
            song == f'{song}...'

        # making volume graphic 
        for volume_percent in spotify_device_resp['devices']:
            volume_percent = volume_percent['volume_percent']
        if volume_percent == 0:
            volume_graphic = '--------'
        elif volume_percent in range(0, 12):
            volume_graphic = '=-------'
        elif volume_percent in range(13, 25):
            volume_graphic = '==------'
        elif volume_percent in range(26, 37):
            volume_graphic = '===-----'
        elif volume_percent in range(38, 50):
            volume_graphic = '====----'
        elif volume_percent in range(51, 62):
            volume_graphic = '=====---'
        elif volume_percent in range(63, 75):
            volume_graphic = '======--'
        elif volume_percent in range(76, 87):
            volume_graphic = '=======-'
        else:
            volume_graphic = '========'

        #getting the remaining playtime on the song 
        song_timestamp = spotify_song_resp['progress_ms']
        song_duration = spotify_song_resp['item']['duration_ms']
        remaining_playtime_ms = song_duration-song_timestamp-13
        remaining_playtime = round(remaining_playtime_ms / 1000, 2)
        if remaining_playtime >= 70.0:
            remaining_playtime = 45.0
    
        #returning variables that the bio update needs
        return song, remaining_playtime, volume_graphic

def rr_bio_change(token, accountId):

    #calling song_info fuction
    song_info_ = song_info(scope, client_id, client_secret, redirect_uri)
    song = song_info_[0] #song
    remaining_playtime = song_info_[1] #remaining_playtime

    #rec room bio request
    bio_resp = requests.get(f'https://accounts.rec.net/account/{accountId}/bio')
    bio_resp_json = bio_resp.json()
    bio_string = bio_resp_json['bio'].split('\n', 3)
    
    #checks if the song has been put into the bio before
    if bio_string[0] == 'Playing:':
        bio = bio_string[3]
    else:
        bio = bio_resp_json['bio']
        print('Detected changed bio')


    if song != config['DONTCHANGE']['song_compare'] or bio != config['BIO']['bio']:
        
        #writing the song/bio to the config file
        if song != config['DONTCHANGE']['song_compare']:
            config['DONTCHANGE']['song_compare'] = song
            writeconfig()
        if bio != config['BIO']['bio']:
            config['BIO']['bio'] = bio
            writeconfig()
            print('Detected changed bio')


        #if theres a index error that means no song is playing
        try:
            volume_graphic = song_info_[2] #volume_graphic
            #request for rec room bio change
            rec_resp = requests.put(f'https://accounts.rec.net/account/me/bio', 
                headers= {"Authorization": token}, 
                data = {'bio':f"Playing:\n{song}\n|Volume: {volume_graphic}|\n{bio}"}
            )
            #renew rr token if the request returning 401
            if rec_resp.status_code == 401:
                token = login(YOURUSERNAME, YOURPASSWORD)
                rec_resp = requests.put(f'https://accounts.rec.net/account/me/bio', headers= {"Authorization": token}, 
                data = {'bio':f"Playing:\n{song}\n|Volume: {volume_graphic}|\n{bio}"}
                )
        except IndexError:
            #request for rec room bio change
            rec_resp = requests.put(f'https://accounts.rec.net/account/me/bio', 
                headers= {"Authorization": token}, 
                data = {'bio':f"Playing:\nNothing\n{bio}"}
            )
            
            #renew token if the request returning 401
            if rec_resp.status_code == 401:
                token = login(YOURUSERNAME, YOURPASSWORD)
                rec_resp = requests.put(f'https://accounts.rec.net/account/me/bio', headers= {"Authorization": token}, 
                data = {'bio':f"Playing:\nNothing\n{bio}"}
                )

        #just showing some info to give some feedback to the user 
        if rec_resp.status_code == 200:
            print(f'Currently playing song: {song}')
            print('Bio change succes!')
            print(f'At {datetime.datetime.now()}')
        else: 
            print('-----')
            print(f'Currently playing song: {song}')
            print('Bio change failed.')
            print(f'Error code:{rec_resp.status_code}')
            print(f'At {datetime.datetime.now()}')
            print('-----')

        #starting loop again after the song ends
    sc.enter(remaining_playtime, 1, rr_bio_change, (token, accountId))

#start the loop 
sc.enter(1.0, 1, rr_bio_change, (token, accountId))
sc.run()
