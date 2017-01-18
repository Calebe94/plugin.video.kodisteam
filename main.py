from subprocess import Popen, PIPE
import sys
from urllib import urlencode
from urlparse import parse_qsl
import xbmcgui
import xbmcplugin

from urllib import urlopen
import xml.etree.ElementTree as ET
import os

# Get the plugin url in plugin:// notation.
_url = sys.argv[0]
# Get the plugin handle as an integer number.
_handle = int(sys.argv[1])

VIDEOS = dict()
LIBRARY = dict()

GET_APP_INFO = "https://steampics-mckay.rhcloud.com/info?apps=200900&prettyprint=1"

ALL_GAMES = 'http://api.steampowered.com/ISteamApps/GetAppList/v0002/?format=xml'
LINUX_GAMES = 'https://raw.githubusercontent.com/SteamDatabase/SteamLinux/master/GAMES.json'

STEAM_WINE_PATH = "/home/calebe945/PlayOnLinux's virtual drives/calebe945/drive_c/Program Files/Steam/steamapps/"
STEAM_LINUX_PATH = "/home/calebe945/.steam/steam/steamapps/"
STEAM_WINE_EXECUTABLE = "/home/calebe945/PlayOnLinux's virtual drives/calebe945/drive_c/Program Files/Steam/Steam.exe"

index = 0
username = ''
password = ''
def Login():
    dialog = xbmcgui.Dialog()
    username = dialog.input('Enter your Username', type=xbmcgui.INPUT_ALPHANUM)
    password = dialog.input('Enter your Password', type=xbmcgui.INPUT_ALPHANUM, option=xbmcgui.ALPHANUM_HIDE_INPUT)

def getAppID(str):
	str1 = str.split('_')
	str2 = str1[1]
	str3 = str2.split('.')
	return str3[0]

def getName(search_appID):
	for appID in range(0,len(LIBRARY['appID'])):
		if search_appID == LIBRARY['appID'][appID]['appID']:
			return LIBRARY['name'][appID]['name']

def getInstalledGames(path):
    AUX_DICT=dict()
    for file in os.listdir(path):
        if file.endswith(".acf"):
            appID = getAppID(file)
            AUX_DICT.setdefault('name',[]).append({'name':getName(appID)})
            AUX_DICT.setdefault('appID',[]).append({'appID':appID})
            header = "http://cdn.edgecast.steamstatic.com/steam/apps/%s/header.jpg"%appID
            AUX_DICT.setdefault('logo',[]).append({'logo':header})
    return AUX_DICT

def getInstalledGames_wine(path):
    AUX_WINE=dict()
    for file in os.listdir(path):
        if file.endswith(".acf"):
            appID = getAppID(file)
            header = "http://cdn.edgecast.steamstatic.com/steam/apps/%s/header.jpg"%appID
            #AUX_WINE.setdefault('WINE',[]).append({'name':getName(appID),'appID':appID,'logo':header})
            AUX_WINE.setdefault('name',[]).append({'name':getName(appID)})
            AUX_WINE.setdefault('appID',[]).append({'appID':appID})
            header = "http://cdn.edgecast.steamstatic.com/steam/apps/%s/header.jpg"%appID
            AUX_WINE.setdefault('logo',[]).append({'logo':header})
    return AUX_WINE

def getInstalledGames_linux(path):
    AUX_LINUX=dict()
    for file in os.listdir(path):
        if file.endswith(".acf"):
            appID = getAppID(file)
            header = "http://cdn.edgecast.steamstatic.com/steam/apps/%s/header.jpg"%appID
            #AUX_LINUX.setdefault('LINUX',[]).append({'name':getName(appID),'appID':appID,'logo':header})
            AUX_LINUX.setdefault('name',[]).append({'name':getName(appID)})
            AUX_LINUX.setdefault('appID',[]).append({'appID':appID})
            header = "http://cdn.edgecast.steamstatic.com/steam/apps/%s/header.jpg"%appID
            AUX_LINUX.setdefault('logo',[]).append({'logo':header})
    return AUX_LINUX

def getOwnedGames(steamid):
    owned_games = "http://steamcommunity.com/id/%s/games?tab=all&xml=1"%steamid
    tree = ET.ElementTree(file=urlopen(owned_games))
    root = tree.getroot()
    
    Owned=dict()
    for game in root.iter('game'):
	    #Owned.setdefault('OWNED',[]).append({'name':game.find('name').text,'appID':game.find('appID').text,'logo':game.find('logo').text})
        Owned.setdefault('name',[]).append({'name':game.find('name').text})
        Owned.setdefault('appID',[]).append({'appID':game.find('appID').text})
        Owned.setdefault('logo',[]).append({'logo':game.find('logo').text})
    return Owned

VIDEOS.setdefault("OWNED",[])
VIDEOS.setdefault("WINE",[])
VIDEOS.setdefault("LINUX",[])
VIDEOS['OWNED'] = getOwnedGames("calebenovequatro")
LIBRARY = VIDEOS['OWNED']
VIDEOS['WINE'] = getInstalledGames_wine(STEAM_WINE_PATH)
VIDEOS['LINUX'] = getInstalledGames_linux(STEAM_LINUX_PATH)

def get_url(**kwargs):
    return '{0}?{1}'.format(_url, urlencode(kwargs))


def get_categories():
    return VIDEOS.iterkeys()


def get_videos(category):
    return VIDEOS[category]


def list_categories():
    categories = get_categories()
    for category in categories:
        list_item = xbmcgui.ListItem(label=category)
        list_item.setArt({'thumb': VIDEOS[category]['logo'][0]['logo'],
                          'icon': VIDEOS[category]['logo'][0]['logo'],
                          'fanart': VIDEOS[category]['logo'][0]['logo']})
        list_item.setInfo('video', {'title': category, 'genre': category})
        url = get_url(action='listing', category=category)
        is_folder = True
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    xbmcplugin.endOfDirectory(_handle)

item_to_play=""

def list_videos(category):
    videos = VIDEOS[category]
    for video in range(0,len(videos['name'])):
        list_item = xbmcgui.ListItem(label=videos['name'][video]['name'])
        list_item.setInfo('video', {'title': videos['name'][video]['name'], 'genre': videos['appID'][video]['appID']})
        list_item.setArt({'thumb':videos['logo'][video]['logo'],'icon':videos['logo'][video]['logo'],'fanart':videos['logo'][video]['logo']})
        #list_item.setProperty('IsPlayable', 'true')
        list_item.setProperty('Games','steam')
        # Example: plugin://plugin.video.example/?action=play&video=http://www.vidsplay.com/vids/crab.mp4
        item_to_play=videos['appID'][video]['appID']
        url = get_url(action='play',video=item_to_play,category=category)
        is_folder = False
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    xbmcplugin.endOfDirectory(_handle)


def play_video(path):
    play_item = xbmcgui.ListItem(path=path)
    xbmcplugin.setResolvedUrl(_handle, True, listitem=play_item)


def router(paramstring):
    params = dict(parse_qsl(paramstring))
    if params:
        if params['action'] == 'listing':
            list_videos(params['category'])
        elif params['action'] == 'play':
            if params['category'] == "LINUX":
                #oi = "steam -applaunch %s"%params['video']
                #os.system(oi)
                process = Popen(['steam','-applaunch',params['video'],'-silent'], stdout=PIPE, stderr=PIPE)
                stdout, stderr = process.communicate()
                pid = process.pid
            elif params['category'] == "WINE":
                process = Popen(['wine',STEAM_WINE_EXECUTABLE,'-applaunch',params['video'],'-silent'], stdout=PIPE, stderr=PIPE)
                stdout, stderr = process.communicate()
                pid = process.pid
                #oi = "wine %s -applaunch %s"%(STEAM_WINE_EXECUTABLE,params['video'])
                #os.system(oi)
            else:
                list_videos(params['category'])
            #play_video(params['video'])
        else:
            raise ValueError('Invalid paramstring: {0}!'.format(paramstring))
    else:
        list_categories()


if __name__ == '__main__':
    router(sys.argv[2][1:])
