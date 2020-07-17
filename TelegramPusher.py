#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import os
import requests
import sys
import time
import re
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor
import json

def getLastPid(ChannelId):
    url = 'https://t.me/s/%s' % ChannelId
    resp = requests.get(url)
    Soup = BeautifulSoup(resp.text,features="html.parser")
    Msgs = Soup.find_all(attrs={"class": "tgme_widget_message_text js-message_text"})
    LastID = '0'
    for Msg in Msgs:
        txt = Msg.get_text()
        if re.match(r'p\d+', txt) != None:
            LastID = txt
    print(LastID)
    return LastID

def genConfig(Path,LastID):
    config = '''{
  "RATINGS": {
    "safe": true,
    "questionable": false,
    "explicit": false
  },
  "STATISTICS": {
    "total_downloads": 0,
    "time_elapsed": 0
  },
  "UPDATING": {
    "previous_newest_id": "%s",
    "SEPARATE": false
  }
}''' % LastID
    with open(os.path.join(Path,'metadata.json'),"w") as txtfile:
        txtfile.write(config)
    print(Path,'Config Done.')


def getPids(Page):
    url = 'https://konachan.net/post?page=%s' % Page
    resp = requests.get(url)
    Soup = BeautifulSoup(resp.text,features="html.parser")
    html = Soup.find("script", string=re.compile(r"Post.register_tags"))
    rawLines = str(html).replace(r'</script>','').replace(r'<script type="text/javascript">','').splitlines()
    pids = []
    for line in rawLines:
        if ('register_tags' not in line) and ('register' in line):
            rawjson = line.replace('Post.register(','')[:-1]
            pid = json.loads(rawjson)['id']
            pids.append(pid)
    return pids


def getPidPage(pid):
    isFindPage = False
    Page = 1
    while not isFindPage :
        pids = getPids(str(Page))
        for i in pids:
            if i <= pid:
                isFindPage = True
            else:
                Page = Page + 1
    return str(Page)

def PushImg(FilePath,BotId,ChannelId):
    PushName =  os.path.split(FilePath)[1].split('.')[1].replace('com_','p')
    url = 'https://api.telegram.org/bot%s/sendPhoto' % BotId
    RawFormData = MultipartEncoder( 
    fields={ 
            'chat_id': '@%s' % ChannelId,
            'photo'  : (os.path.split(FilePath)[1], open(FilePath, 'rb'), 'application/octet-stream'),
            'caption': PushName
    } )
    def UploadBar(monitor,Size):
        return 1
    FormData = MultipartEncoderMonitor(RawFormData, lambda e:UploadBar(e,RawFormData.len))
    resp = requests.post(url, data=FormData, headers={'Content-Type': FormData.content_type})
    print(resp.text)
    print('%s Finish.' % PushName)

def PushDoc(FilePath,BotId,ChannelId):
    PushName =  os.path.split(FilePath)[1].split('.')[1].replace('com_','p')
    url = 'https://api.telegram.org/bot%s/sendDocument' % BotId
    RawFormData = MultipartEncoder( 
    fields={ 
            'chat_id': '@%s' % ChannelId,
            'document'  : (os.path.split(FilePath)[1], open(FilePath, 'rb'), 'application/octet-stream'),
            'caption': PushName
    } )
    def UploadBar(monitor,Size):
        return 1
    FormData = MultipartEncoderMonitor(RawFormData, lambda e:UploadBar(e,RawFormData.len))
    resp = requests.post(url, data=FormData, headers={'Content-Type': FormData.content_type})
    print(resp.text)
    print('%s Finish.' % PushName)

def PushMsg(Msg,BotId,ChannelId):
    url = 'https://api.telegram.org/bot%s/sendMessage?chat_id=@%s&text=%s' % (BotId,ChannelId,Msg)
    resp = requests.get(url)
    print(resp.text)
    print('%s Pushed.' % Msg)

def Renamer(Path):
    files = os.listdir(Path)
    for file in files:
        if 'Konachan.com_' in file:
            newName = 'Konachan.com_' + file.split('_')[1] + '.' + file.split('.')[-1]
            newName = os.path.join(Path,newName)
            Name = os.path.join(Path,file)
            os.rename(Name,newName)

def Deleter(Path,LastPid):
    files = os.listdir(Path)
    LastPid = int(LastPid[1:])
    for file in files:
        if 'Konachan.com_' in file:
            pid = int(file.split('.')[1].split('_')[1])
            if pid <= LastPid:
                os.remove(os.path.join(Path,file))

def getTime(tz):
    from datetime import datetime,timedelta,timezone
    date = datetime.utcnow().replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=tz))).strftime('%Y{y}%m{m}%d{d}').format(y='年', m='月', d='日')
    time = datetime.utcnow().replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=tz))).strftime('%H:%M:%S')
    return [date,time]

def Pusher(Path,BotId,ChannelId):
    files = []
    rawfiles = os.listdir(Path)
    for file in rawfiles:
        if 'Konachan.com_' in file:
            files.append(file)
    files.sort(key= lambda x:int(x.split('.')[1].split('_')[1]))
    CurrentDate = getTime(8)[0]
    print('Push time is',CurrentDate,getTime(8)[1])
    PushMsg(CurrentDate,BotId,ChannelId)
    time.sleep(4)
    for file in files:
        PicPath = os.path.join(Path,file)
        if os.path.getsize(PicPath)/1024/1024 < 9.9:
            PushImg(PicPath,BotId,ChannelId)
            time.sleep(4)
        PushDoc(PicPath,BotId,ChannelId)
        time.sleep(4)
            
        
if __name__ == '__main__':
    os.mkdir('pic')
    Path = os.path.join(os.getcwd(),'pic') + os.sep
    BotId= sys.argv[1]
    ChannelId = sys.argv[2]
    LastPid = getLastPid(ChannelId)
    if LastPid == '0':
        print('First run, download 5 page.')
        os.system(r'python3 konadl_cli.py -o %s -s -n 5' %Path)
    else :
        Page = getPidPage(int(LastPid[1:]))
        print('Last Pid is %s in page %s.' % (LastPid,Page))
        os.system(r'python3 konadl_cli.py -o %s -s -n %s' % (Path,Page) )
    Renamer(Path)
    if LastPid != '0':
        Deleter(Path,LastPid)
    Pusher(Path,BotId,ChannelId)