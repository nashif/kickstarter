#!/usr/bin/python

import urllib2
from datetime import date
from xml.etree.ElementTree import ElementTree

url = "http://download.meego.com/snapshots/1.1.90.8.20110317.88/builddata/image-configs.xml"
f = urllib2.urlopen(url)
tree = ElementTree()
tree.parse(f)
configs = tree.findall('config')
for c in configs:
    planned = False
    name = c.find('name').text
    dow = date.today().weekday()
    if c.find('schedule').text != '':
        schedule = c.find('schedule').text
        if schedule == '*':
            planned = True
        elif schedule in ["0","1","2","3","4","5","6"] and int(schedule) == dow:
            planned = True
    else:
        planned = False

    if planned:
        print "%s is scheduled to be created today" %name
    else:
        print "%s is not scheduled to be created today" %name

