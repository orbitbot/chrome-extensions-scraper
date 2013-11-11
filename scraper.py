from bs4 import BeautifulSoup
from string import strip

import requests
import pprint

base_url = 'http://developer.chrome.com/extensions/'
page_url = base_url + 'samples.html'

r = requests.get(page_url)

soup = BeautifulSoup(r.text)

examples = []

for index, sample_section in enumerate(soup('div', class_='sample')):
    project = {}
    project['name'] = sample_section.a.string
    project['desc'] = (sample_section.a.parent.next_sibling).strip()
    project['zip'] = sample_section.a.get('href')

    doc = []
    files = []

    links = sample_section('ul')
    for index, item in enumerate(links[0].select('li code a')):
        doc.append({'call': item.string,
                    'link': item.get('href')})

    for index, item in enumerate(links[1].select('li code a')):
        files.append({'call': item.string,
                      'link': item.get('href')})
    project['doc'] = doc
    project['files'] = files

    examples.append(project)

pprint.pprint(examples[0])