from spotipy.oauth2 import SpotifyOAuth
from recnetlogin import RecNetLogin
from dotenv import load_dotenv
import configparser
import sched, time
import requests
import spotipy
import sys
import os


# ill be honest i dont remeber what this does all i know if i delete it it doesnt work
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

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
    config['BIO']['savebio'] = 'false'
    config['BIO']['bio'] = ''

    config.add_section('LOGIN')
    config['LOGIN']['storelogin'] = 'false'
    config['LOGIN']['YOURUSERNAME'] = ''
    config['LOGIN']['YOURPASSWORD'] = ''
    with open("config.ini", 'w') as f: 
        config.write(f)


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
            with open("config.ini", 'w') as configfile:
                config.write(configfile)
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
        with open("config.ini", 'w') as configfile:
            config.write(configfile)
        
#setting spotipy auth stuff
client_id = os.environ['client_id']
client_secret = os.environ['client_secret']
redirect_uri = 'http://localhost:7777/callback'
scope = 'user-read-currently-playing'

#asking user if theyd like stuff added to their bio
bio = ''
bioconfirm = 'n'
def bioconfig(bioconfirm):
    while bioconfirm == 'n':
        bio = input('Enter any extra stuff you would like to add to your bio(press enter for none): ') 
        print('Listening to:')
        print('Example song by Example')
        print(bio)
        bioconfirm = input('Confirm you want your bio to this(y/n)?')
        while bioconfirm not in {'y', 'n'}:
            print('Enter y/n')
            bioconfirm = input('Confirm you want your bio to this(y/n)?')

    if bio not in {'', ' '}:
        savebio = input('Would you like the bio you entered to be saved next time you run the program(y/n)? ')
        while savebio not in {'y', 'n'}:
            print('Enter y/n')
            savebio = input('Would you like the bio you entered to be saved next time you run the program(y/n)? ')
        if savebio == 'y':
            config['BIO']['savebio'] = 'true'
            config['BIO']['bio'] = bio
        else:
            config['BIO']['savebio'] = 'false'

    with open("config.ini", 'w') as configfile:
        config.write(configfile)

    return bio
config.read("config.ini")

#getting saved bio if its there
if config.getboolean('BIO', 'savebio') == False:
    bio = bioconfig(bioconfirm)
elif config.getboolean('BIO', 'savebio') == True: 
    print('Found saved bio!')
    print('Listening to:')
    print('Example song by Example')
    print(config['BIO']['bio'])
    bioconfirm = input('Confirm you want your bio to be this(y/n)?')
    while bioconfirm not in {'y', 'n'}:
        print('Enter y/n')
        bioconfirm = input('Confirm you want your bio to be this(y/n)?')
    if bioconfirm == 'n':
        bioconfig(bioconfirm)
    else: 
        bio = config['BIO']['bio']

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
    spotify_resp = sp.current_user_playing_track()

    #check to see if song is being played and handling for if not
    if spotify_resp == None or spotify_resp['is_playing'] == False:
        song = 'Not Playing Any Songs Currently'
        return song, 45.0

    #formating the song name 
    track_name = spotify_resp['item']['name']
    artists = [artist for artist in spotify_resp['item']['artists']]
    artist_names = ', '.join([artist['name'] for artist in artists])
    song = f'{track_name} by {artist_names}!'

    #getting the remaining playtime on the song 
    song_timestamp = spotify_resp['progress_ms']
    song_duration = spotify_resp['item']['duration_ms']
    remaining_playtime_ms = song_duration-song_timestamp-13
    remaining_playtime = round(remaining_playtime_ms / 1000, 2)
    if remaining_playtime >= 70.0:
        remaining_playtime = 45.0
    
    #returning variables that the bio update needs
    return song, remaining_playtime

def rr_bio_change(token, bio):

    #calling song_info fuction
    song_info_ = song_info(scope, client_id, client_secret, redirect_uri)
    song = song_info_[0] #song
    remaining_playtime = song_info_[1] #remaining_playtime

    if song != config['DONTCHANGE']['song_compare']:
        
        #writing the song to the config file
        config['DONTCHANGE']['song_compare'] = song
        with open("config.ini", 'w') as configfile:
            config.write(configfile)
        
        #request for rec room bio change
        rec_resp = requests.put(f'https://accounts.rec.net/account/me/bio', 
            headers= {"Authorization": token}, 
            data = {'bio':f"Listening To:\n{song}\n{bio}"}
        )
        
        #renew token if the request returning 401
        if rec_resp.status_code == 401:
            token = login(YOURUSERNAME, YOURPASSWORD)
            rec_resp = requests.put(f'https://accounts.rec.net/account/me/bio', headers= {"Authorization": token}, 
            data = {'bio':f"Listening To:\n{song}\n{bio}"})

        
        #just showing some info to give some feedback to the user 
        if rec_resp.status_code == 200:
            print(f'Currently playing song: {song}')
            print('Bio change succes!')
        else: 
            print('-----')
            print(f'Currently playing song: {song}')
            print('Bio change failed.')
            print(f'Error code:{rec_resp.status_code}')
            print('-----')

        #starting loop again after the song ends
    sc.enter(remaining_playtime, 1, rr_bio_change, (token, bio))

#start the loop 
sc.enter(1.0, 1, rr_bio_change, (token, bio))
sc.run()
