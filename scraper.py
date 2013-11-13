from string import strip

from bs4 import BeautifulSoup
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
    zipfile = sample_section.a.get('href')
    project['zip'] = zipfile
    project['folder'] = zipfile[ zipfile.rfind('/') + 1 : zipfile.rfind('.zip')]

    doc = []
    files = []

    links = sample_section('ul')
    for index, item in enumerate(links[0].select('li code a')):
        doc.append({'call': item.string,
                    'link': base_url + item.get('href')})

    for index, item in enumerate(links[1].select('li code a')):
        files.append({'call': item.string,
                      'link': base_url + item.get('href')})
    project['doc'] = doc
    project['files'] = files

    examples.append(project)

pprint.pprint(examples[0])

bullet_list_template = '* [%(call)s](%(link)s)'
project_list_template = '* <a href="%(folder)s">%(name)s</a>'
readme_template = """
%(name)s
=======

%(desc)s

[zipfile](http://developer.chrome.com/extensions/%(zip)s)

Content is licensed under the [Google BSD License](http://code.google.com/google_bsd_license.html).

Calls
-----

"""

readme = readme_template % examples[0]
bullets = []
for item in examples[0]['doc']:
    bullets.append(bullet_list_template % item)

readme += '\n'.join(bullets)

print readme