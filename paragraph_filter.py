import os, re
from nltk.corpus import stopwords
import csv

rootdir = 'fetched_data'

if not os.path.isdir('output'):
    os.makedirs('outpu')

termDict = {}
for files in os.listdir(rootdir):
	if '.html' in files:
		f = open('fetched_data/' + files, 'r')
		readfile = f.read()
		p = re.compile('<.*?>')
		li = p.findall(readfile)
		for instance in li:
			readfile = readfile.replace(instance, '')
		p = re.compile('\[[0-9]*?\]|/|\.|\(|\)|,|\"|\−|\;|\[|\]|\*|\:|\~')
		li = p.findall(readfile)
		for instance in li:
			readfile = readfile.replace(instance, '')
		wordsRep = readfile.split()
		wordsRep = [word.lower() for word in wordsRep]
		words = []
		for i in wordsRep:
			if i not in words:
				words.append(i)
		stop = stopwords.words('english')
		for word in words:
			if word in stop:
				words.remove(word)
			elif word in termDict:
				termDict[word].append(files)
			else:
				termDict[word] = [files]
keys = open("keys", "w")
for key, val in termDict.items():
	if len(key.encode('utf-8')) <= 255:
		w = csv.writer(open("output/"+ key +".csv", "w"))
		w.writerow(val)
		keys.write(key+"\n")
