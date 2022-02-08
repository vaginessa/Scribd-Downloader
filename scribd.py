#!/bin/python

from bs4 import BeautifulSoup
import requests
import sys
import shutil
import os

#print(len(sys.argv)) 
os.chdir(sys.path[0])

if len(sys.argv) ==1:
	print("Usage: sudo python scribd.py <link of scribd document>") 
	print("For selectable PDFs:") 
	print("example: sudo python scribd.py https://www.scribd.com/document/55949937/33-Strategies-of-War") 
	print("For PDFs containing Images; use the -p option:") 
	print("example: sudo python scribd.py http://scribd.com/doc/17142797/Case-in-Point -p") 
	exit()

response = requests.request(method='GET', url=sys.argv[1])
soup = BeautifulSoup(response.text, 'html.parser')
extraction = ''
train = 1

title = soup.find('title').get_text().replace(' ', '_')
print(soup.find('title').get_text()) 

if len(sys.argv) <=2:
	if os.path.exists(title + '.txt'):
		os.remove(title + '.txt')
else:
	if not os.path.exists(title):
		os.makedirs(title)

js_text = soup.find_all('script', type='text/javascript')
for opening in js_text:
	for inner_opening in opening:
		portion1 = inner_opening.find('https://')
		if not portion1 == -1:
			portion2 = inner_opening.find('.jsonp')
			jsonp = inner_opening[portion1:portion2+6]
			if not jsonp == '':
				if len(sys.argv) <=2:
					#print(jsonp) 
					response = requests.request(method='GET', url=jsonp)
					page_no = response.text[11:12]
					response_head =  (response.text).replace('window.page' + page_no + '_callback(["', '').replace('\\n', '').replace('\\', '').replace('"]);', '')
					#print(response_head) 
					soup_content = BeautifulSoup(response_head, 'html.parser')
					#print(soup_content.get_text().encode('utf-8')) 
					for x in soup_content.find_all('span', {'class':'a'}):
						xtext = x.get_text().encode('utf-8')
						print(xtext) 
						extraction = extraction + xtext + '\n'
				else:
					replacement = jsonp.replace('/pages/', '/images/').replace('jsonp', 'jpg')
					#print(replacement) 
					print('Downloading page ' + str(train)) 
					response = requests.get(replacement, stream=True)
					with open(title + '/pic' + str(train) + '.jpg', 'wb') as out_file:
						shutil.copyfileobj(response.raw, out_file)
					del response
					train+=1

if len(sys.argv) <=2:
	with open(title + '.txt', 'w') as feed:
		feed.write(extraction)
