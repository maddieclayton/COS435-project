import re, csv, sys

termDict1 = {}
for key, val in csv.reader(open("output.csv")):
	result = []
	p = re.compile('\'.*?\'')
	li = p.findall(val)
	for instance in li:
		result.append(instance[1:-1])
	termDict1[key] = result

query = sys.argv[1]
queryWords = query.split()
scoreDict = {}
for word in queryWords:
	if word in termDict1:
		listDocs = termDict1[word]
	else:
		listDocs = {}
	for doc in listDocs:
		if doc in scoreDict:
			scoreDict[doc] = scoreDict[doc] + 1/len(listDocs)
		else:
			scoreDict[doc] = 1/len(listDocs)

result = max(scoreDict, key=scoreDict.get)
print (result)