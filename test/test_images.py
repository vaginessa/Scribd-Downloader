import requests
from bs4 import BeautifulSoup
import scribdl
import os


URL = 'http://scribd.com/doc/17142797/Case-in-Point'
images = True


def test_jsonp():
    expect_jsonp = '/6uj1tnfc00bk97m/pages/'

    response = requests.get(url=URL).text
    soup = BeautifulSoup(response, 'html.parser')

    js_text = soup.find_all('script', type='text/javascript')
    inner_opening = js_text[24].get_text()

    portion1 = inner_opening.find('https://')
    portion2 = inner_opening.find('.jsonp')
    global jsonp
    jsonp = inner_opening[portion1:portion2+6]

    print(jsonp)
    print(expect_jsonp)
    assert expect_jsonp in jsonp


def test_image():
    expect_image = True
    scribdl.save_image(jsonp, 'testimage.jpg')
    image = os.path.isfile('testimage.jpg')

    if image:
        os.remove('testimage.jpg')

    assert image == expect_image
