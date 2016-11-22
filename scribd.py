#~/bin/python
 # -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import json
import requests
import sys

response = requests.request(method='GET', url=sys.argv[1])
#print len(sys.argv)
pre_soup = response.text

soup = BeautifulSoup(pre_soup, 'html.parser')
last_xtext = ''

js_text = soup.find_all('script', type="text/javascript")
for opening in js_text:
	for inner_opening in opening:
		portion1 = inner_opening.find('https://')
		if not portion1 == -1:
			portion2 = inner_opening.find('.jsonp')
			jsonp = inner_opening[portion1:portion2+6]
			if not jsonp == '':
				if len(sys.argv) <=2:
					#print jsonp
					response = requests.request(method='GET', url=jsonp)
					soup_content = BeautifulSoup(response.text, 'html.parser')
					for x in soup_content.find_all('span'):
						xtext = x.get_text().encode('utf-8')
						if not xtext == '':
							if not xtext == last_xtext:
								print xtext
							last_xtext = xtext
				else:
					replacement = jsonp.replace('/pages/', '/images/').replace('.jsonp', sys.argv[2])
					print replacement
