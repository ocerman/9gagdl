import urllib
import urllib.request
import json
import datetime
import sys
import itertools
import os
from lxml import html
import time

if len(sys.argv) == 0:
	print("Usage: python 9gagdl.py username")
	exit();

user = sys.argv[1]
host = 'https://9gag.com'
likespath = '/likes'
gagpath = '/gag'
likesurl = host + '/u/' + user + likespath
downloadDir = "download/" + user + "/" + datetime.datetime.now().strftime("%Y-%m-%d--%H-%M-%S") 
sleepLength = 0.1

downloadUrl = 'https://img-9gag-fun.9cache.com/photo/'


def downloadData(url):
	request = urllib.request.Request(url);

	request.add_header('Accept', 'application/json')
	request.add_header('X-Requested-With', 'XMLHttpRequest')

	data = '';
	try:
		jsontxt = urllib.request.urlopen(request).read().decode()
		data = json.loads(jsontxt)
	except:
		print('File cannot be downloaded');
		
	if not 'okay' in data or not data['okay']:
		input('Wrong server response');
		exit();
	
	return data

def getGags(data, gags):
		
	for gagId in data['ids']:
		if gagId in data['items']:
			gagHtml = data['items'][gagId]
			title = ''
			type = 'image'
			tags = []
			
			doc = html.fromstring(gagHtml)
			htmlheader = doc.cssselect("h2");
			if len(htmlheader) >= 1:
				title = htmlheader[0].text_content().strip()
			
			htmlvideo = doc.cssselect("video");
			if len(htmlvideo) >= 1:
				type = 'video'
				
			htmltags = doc.cssselect(".post-tag a");
			for htmltag in htmltags:
				tags.append(htmltag.text_content().strip())
			
			gags.append([gagId, type, title, tags]);

	if 'loadMoreUrl' in data:
		return host + data['loadMoreUrl'];
	
	return None

def saveGags(page, gags):
	i = 1;
	for gag in gags:
		
		sys.stdout.write('-')
		sys.stdout.flush()
		
		id = gag[0]
		type = gag[1]
		title = gag[2]
		tags = gag[3]
		ok = False
		
		prefix = 'P' + '{0:04d}'.format(page) + '.G' + '{0:02d}'.format(i) + '.'
		fileName = id + "_700b.jpg";
		if type == "video":
			fileName = id + "_460sv.mp4"
		
		infoFilePath = downloadDir + "/" + prefix + id + ".txt";
		
		try:
			urllib.request.urlretrieve(downloadUrl + fileName, downloadDir + "/" + prefix + fileName)
			ok = True
			sys.stdout.write('\b=')
		except:
			sys.stdout.write('\bX') 
		
		sys.stdout.flush()
			
		if ok:
			infoFile = open(infoFilePath, 'w', encoding='utf-8')
			infoFile.write('ID: ' + id + '\n');
			infoFile.write('URL: ' + host + gagpath + '/' + id + '\n');
			infoFile.write('Title: ' + title + '\n');
			infoFile.write('Tags: ' + ','.join(tags) + '\n');
			infoFile.close();
		
		time.sleep(sleepLength);
		i += 1
		
		
if not os.path.exists(downloadDir):
	os.makedirs(downloadDir)

print("Downloading gags to " + downloadDir);
print();

nexturl = likesurl
i = 1
	
while True:
	print("Page ", i);
	gags = []
	
	data = downloadData(nexturl)
	nexturl = getGags(data, gags)
	saveGags(i, gags);
	
	print()
	
	i += 1
	
	if not nexturl:
		break
	
	if not nexturl.startswith(likesurl):
		break;
	
print('End')


