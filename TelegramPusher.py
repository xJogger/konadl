#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import os
import requests
import sys
import time
import re
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor

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

def Pusher(Path,BotId,ChannelId):
	files = []
	rawfiles = os.listdir(Path)
	for file in rawfiles:
		if 'Konachan.com_' in file:
			files.append(file)
	files.sort(key= lambda x:int(x.split('.')[1].split('_')[1]))
	CurrentDate = time.strftime("%Y{y}%m{m}%d{d}", time.localtime()).format(y='年', m='月', d='日')
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
	'''
	LastPid = getLastPid(ChannelId)
	if LastPid == '0':
		print(r'python3 konadl_cli.py -o %s -s -n 1' %Path)
		os.system(r'python3 konadl_cli.py -o %s -s -n 1' %Path)
	else :
		genConfig(Path,LastPid)
		print(r'python3 konadl_cli.py -o %s --update' %Path)
		os.system(r'python3 konadl_cli.py -o %s --update' %Path)
	genConfig(Path,LastPid)
	'''
	os.system(r'python3 konadl_cli.py -o %s -s -n 2' %Path)
	Renamer(Path)
	Pusher(Path,BotId,ChannelId)
	