import json
from bs4 import BeautifulSoup
from datetime import datetime
import Queue
from threading import Thread
import unicodedata
import requests 
import os,sys
import re
import urlmarker
import unidecode
import urlparse

reload(sys)
sys.setdefaultencoding("utf-8")

def strip_str(s):
    s = s.strip("\n")
    s = s.strip()
    s = s.rstrip()
    s = s.strip(" ")
    s = s.replace(" ", "")
    return s

def slugify(text):
    text = unidecode.unidecode(text).lower()
    return re.sub(r'\W+', '-', text)

def find_str(s, char):
    index = 0

    if char in s:
        c = char[0]
        for ch in s:
            if ch == c:
                if s[index:index+len(char)] == char:
                    return index

            index += 1

    return -1

def download(url, savepath):
	r = requests.get(url)

	with open(savepath, 'wb') as f:  
		f.write(r.content)

def getMp4(url):
	ob = {}
	result = requests.get(url)

	soup = BeautifulSoup(result.text, "html.parser")
	video_title = soup.title.string
	slug_title = slugify(video_title)
	print slug_title
	startTime = datetime.now()

	scripts = soup.findAll("script")
	text = scripts[len(scripts)-5].text
	text = strip_str(text)
	text = text.strip(" ")
	origin_text = text

	first_po = find_str(text, 'playlist=[{\ntitle')
	json_string = text[first_po+9:]
	second_po = find_str(json_string, '}]')
	json_string = json_string[:second_po+2]
	# print json_string
	link_list = re.findall(urlmarker.WEB_URL_REGEX,json_string)
	# print link_list
	link_download = link_list[len(link_list)-1]
	if "https" not in link_download:
		link_download = 'https://' + link_download
		pass
	
	print link_download
	download(link_download, 'download/' + folder_name + '/' + slug_title + '.mp4')
	print datetime.now()-startTime
	return text

def getListPage(url):
	result = requests.get(url)
	soup = BeautifulSoup(result.text, "html.parser")
	ul = soup.find("ul", class_="pagination")
	if ul is not None:
		list_li = ul.findAll("li")
		last_li = list_li[len(list_li)-1]
		a_tag = last_li.find("a")
		url = a_tag.get("href")
		page_number = url[len(url)-1:]
		base_url = "https://tv.zing.vn/" + url[:len(url)-1]
		for x in xrange(1,int(page_number)+1):
			list_link_page.append(base_url+str(x))
			pass
		pass
	else:
		list_link_page.append(url)
	url_path = urlparse.urlparse(url).path
	paths = os.path.split(url_path)
	folder_name = str(paths[1])
	directory = 'download/' + folder_name
	if not os.path.exists(directory):
		os.makedirs(directory)
	return folder_name

def getLink(url_page):
	# print "link page: " + url_page
	result = requests.get(url_page)
	soup = BeautifulSoup(result.text, "html.parser")
	divs = soup.findAll("div", class_="box-description")
	for div in divs:
		link = div.find("a")
		# list_link.append("https://tv.zing.vn/"  + link.get("href"))
		list_link.insert(0, "https://tv.zing.vn/"  + link.get("href"))
		pass
	pass

if len(sys.argv)<2:
	print "please insert link"
else:
	url = sys.argv[1]
	print url
	# validateUrl(url)
	list_link_page = []
	list_link = []
	list_mp4 = []
	folder_name = getListPage(url)
	# getListPage("https://tv.zing.vn/series/ouran-high-school-host-club")
	print folder_name
	# print list_link_page
	for link_page in list_link_page:
		getLink(link_page)
		pass
	for link in list_link:
		# print link
		getMp4(link)
# # getMp4("https://tv.zing.vn/video/id/IWZ97A87.html")
# with open('zing.json', 'w') as outfile:  
#     for link in list_mp4:
#     	outfile.write(link + '\n')

# getMp4(77)