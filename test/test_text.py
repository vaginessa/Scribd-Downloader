import requests
from bs4 import BeautifulSoup
import scribd

URL = 'https://www.scribd.com/document/55949937/33-Strategies-of-War'
images = False

response = requests.get(url=URL).text
soup = BeautifulSoup(response, 'html.parser')

js_text = soup.find_all('script', type='text/javascript')
inner_opening = js_text[16].get_text()

portion1 = inner_opening.find('https://')
portion2 = inner_opening.find('.jsonp')
jsonp = inner_opening[portion1:portion2+6]

def test_jsonp():
    expect_json = 'https://html2-f.scribdassets.com/8u7q15n1q8z07to/pages/1-a9de44b065.jsonp'
    assert jsonp == expect_json
