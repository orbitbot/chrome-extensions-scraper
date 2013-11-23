from string import strip
from operator import itemgetter
import os
import StringIO
import zipfile
import tempfile
import shutil

from bs4 import BeautifulSoup
import requests


base_url = 'http://developer.chrome.com/extensions/'
page_url = base_url + 'samples.html'


## Scrape data from Examples page

r = requests.get(page_url)

soup = BeautifulSoup(r.text)

examples = []

for index, sample_section in enumerate(soup('div', class_='sample')):
    project = {}
    project['name'] = sample_section.a.string
    project['desc'] = (sample_section.a.parent.next_sibling).strip()
    zip_url = sample_section.a.get('href')
    project['zip'] = zip_url
    project['folder'] = zip_url[ zip_url.rfind('/') + 1 : zip_url.rfind('.zip')]

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


## Setup subfolder for new git repo

subfolder = 'chrome-extensions-examples'

os.mkdir(subfolder)


## Download and extract example projects

bullet_list_template = '* [%(call)s](%(link)s)'
readme_template = """
%(name)s
=======

%(desc)s

[Zipfile](http://developer.chrome.com/extensions/%(zip)s)

Content is licensed under the [Google BSD License](http://code.google.com/google_bsd_license.html).

Calls
-----

"""

for project in examples:

    project_path = os.path.join(subfolder, project['folder'])
    
    tmp_dir = tempfile.mkdtemp()

    r = requests.get(base_url + project['zip'])
    if r.ok:
        z = zipfile.ZipFile(StringIO.StringIO(r.content))
        z.extractall(path=tmp_dir)

    try:
        shutil.copytree(os.path.join(tmp_dir, project['folder']), project_path)
    except OSError, e:
        if e.errno == 17:
            num = 1
            while True:
                try:
                    tmp_path = project_path + '_' + str(num)
                    print 'Got existing subfolder: "' + project_path + '", trying "' + tmp_path + ""
                    shutil.copytree(os.path.join(tmp_dir, project['folder']), tmp_path)
                    project_path = tmp_path
                    break
                except OSError, e:
                    if e.errno == 17:
                        num += 1
                        continue
                    else:
                        break
                        raise e
        else:
            raise e

    shutil.rmtree(tmp_dir)

    project['subfolder'] = os.path.split(project_path)[1]

    bullets = []
    for item in project['doc']:
        bullets.append(bullet_list_template % item)

    readme = readme_template % project
    readme += '\n'.join(bullets)

    with open(os.path.join(project_path, 'README.md'), 'a') as outfile:
        outfile.write(readme)


## Write main readme with correct project subfolders

project_list_template = '* [%(name)s](/%(subfolder)s/)'
project_list = []

for project in sorted(examples, key = itemgetter('name')):
    project_list.append(project_list_template % project)

main_readme = """
chrome-extensions-examples
==========================

The [Chrome Extensions examples](http://developer.chrome.com/extensions/samples.html) did not 
exist as a Git repository, and browsing both the samples page and the VCViewer did not seem particularly
handy. So, I decided to scrape the content into this repository for easier browsing and (possible)
editing.

If you would like to clone a part of this repository, use git 
[sparse checkouts](http://jasonkarns.com/blog/subdirectory-checkouts-with-git-sparse-checkout/).

You can find the scraper used to generate this repository (except for a `git init` and push) 
on [github](https://github.com/orbitbot/chrome-extension-scraper).


Content is licensed under the [Google BSD License](http://code.google.com/google_bsd_license.html).


Example projects
----------------

"""

main_readme += '\n'.join(project_list)

with open(os.path.join(subfolder, 'README.md'), 'w') as outfile:
    outfile.write(main_readme)
