#!/usr/bin/env python

from bs4 import BeautifulSoup
import requests
import sys
import shutil
import os

os.chdir(sys.path[0])

if len(sys.argv) == 1:
	print('Usage: sudo python scribd.py <link of scribd document>')
	print("")
	print('For selectable PDFs:')
	print('- example: sudo python scribd.py https://www.scribd.com/document/55949937/33-Strategies-of-War')
	print("")
	print('For PDFs containing Images; use the -p option:')
	print('- example: sudo python scribd.py http://scribd.com/doc/17142797/Case-in-Point -p')
	exit()
	
def fix_encoding(query):
	if sys.version_info > (3,0):
		return query
	else:
		return query.encode('utf-8')

response = requests.request(method='GET', url=sys.argv[1])
soup = BeautifulSoup(response.text, 'html.parser')
train = 1

title = soup.find('title').get_text().replace(' ', '_')
print(soup.find('title').get_text())

if len(sys.argv) <= 2:
	if os.path.exists(title + '.txt'):
		os.remove(title + '.txt')
else:
	if not os.path.exists(title):
		os.makedirs(title)
print("")

js_text = soup.find_all('script', type='text/javascript')
for opening in js_text:
	for inner_opening in opening:
		portion1 = inner_opening.find('https://')
		if not portion1 == -1:
			portion2 = inner_opening.find('.jsonp')
			jsonp = inner_opening[portion1:portion2+6]
			if not jsonp == '':
				if len(sys.argv) <= 2:
					response = requests.request(method='GET', url=jsonp)
					page_no = response.text[11:12]
					response_head =  (response.text).replace('window.page' + page_no + '_callback(["', '').replace('\\n', '').replace('\\', '').replace('"]);', '')
					soup_content = BeautifulSoup(response_head, 'html.parser')
					for x in soup_content.find_all('span', {'class':'a'}):
						xtext = fix_encoding(x.get_text())
						print(xtext)
						extraction = xtext + '\n'
						with open((title + '.txt'), 'a') as feed:
							feed.write(extraction)
				else:
					replacement = jsonp.replace('/pages/', '/images/').replace('jsonp', 'jpg')
					print('Downloading page ' + str(train))
					response = requests.get(replacement, stream=True)
					with open(title + '/pic' + str(train) + '.jpg', 'wb') as out_file:
						shutil.copyfileobj(response.raw, out_file)
					del response
					train += 1
