from bs4 import BeautifulSoup

import requests

url = 'http://developer.chrome.com/extensions/samples.html'

r = requests.get(url)

soup = BeautifulSoup(r.text)

for sample_section in soup('div', class_='sample'):
    project_name = sample_section.a.string
    project_desc = sample_section.a.parent.next_sibling
    zip_url = sample_section.a.get('href')

    print project_name
    print project_desc.strip()
    print zip_url
