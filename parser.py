import urllib2
import re


resp = urllib2.urlopen('https://en.wikipedia.org/wiki/M')
page = resp.read()

p = re.compile('href="/wiki/.*?"')
li = p.findall(page)

for s in li:
	print 'https://en.wikipedia.org/' + s[7:]