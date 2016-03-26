import urllib.request
import re

resp = urllib.request.urlopen('https://en.wikipedia.org/wiki/M')
page = resp.read()

p = re.compile(b'href="/wiki/.*?"')
li = p.findall(page)

for s in li:
	print ('https://en.wikipedia.org/' + s[7:-1].decode("utf-8"))