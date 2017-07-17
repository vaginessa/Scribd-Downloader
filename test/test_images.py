import requests
from bs4 import BeautifulSoup
import scribd

URL = 'http://scribd.com/doc/17142797/Case-in-Point'
images = True

response = requests.get(url=URL).text
soup = BeautifulSoup(response, 'html.parser')

title = soup.find('title').get_text()
title = scribd.sanitize_title(title)

js_text = soup.find_all('script', type='text/javascript')
inner_opening = js_text[22].get_text()

portion1 = inner_opening.find('https://')
portion2 = inner_opening.find('.jsonp')
jsonp = inner_opening[portion1:portion2+6]


def test_jsonp():
    expect_jsonp = 'https://html1-f.scribdassets.com/6uj1tnfc00bk97m/pages/4-8e53969a8b.jsonp'
    assert jsonp == expect_jsonp

def test_image():
    expect_code = 200
    replacement = jsonp.replace('/pages/', '/images/').replace('jsonp', 'jpg')
    response = requests.get(replacement, stream=True)
    code = response.status_code
    assert code == expect_code
