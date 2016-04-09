import os, re
from nltk.corpus import stopwords
import csv

rootdir = 'fetched_data_small'

termDict = {}
for files in os.listdir(rootdir):
	if '.html' in files:
		f = open('fetched_data_small/' + files, 'r')
		readfile = f.read()
		p = re.compile('<.*?>|\[[0-9]*?\]|\(|\)|\,|\.')
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

w = csv.writer(open("output.csv", "w"))
for key, val in termDict.items():
    w.writerow([key, val])
#for line in termDict:
#	print (line, termDict[line])
